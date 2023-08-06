"""cubicweb vcs file source

view a version control system content as entities

:organization: Logilab
:copyright: 2007-2009 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
"""
__docformat__ = "restructuredtext en"

from os.path import split, join

from yams import ValidationError
from logilab.mtconverter import guess_mimetype_and_encoding

from cubicweb import QueryError, typed_eid
from cubicweb.server.sqlutils import SQL_PREFIX
from cubicweb.server.sources.rql2sql import SQLGenerator
from cubicweb.server.sources.extlite import (SQLiteAbstractSource,
                                             ConnectionWrapper)

from cubes.vcsfile.repo import VCS_REPOS

def get_vcs_source(repo):
    """return the vcs source of the repository (can only have one)"""
    vcssources = [s for s in repo.sources if isinstance(s, VCSSource)]
    assert len(vcssources) == 1, "check your source configuration (hint: [vcs]\nadapter=vcsfile)"
    return vcssources[0]

def set_at_revision(session, reid):
    rqlexec = session.unsafe_execute
    rqlexec('SET VC at_revision REV '
            'WHERE REV eid %(rev)s, VC from_revision REV',
            {'rev': reid}, 'rev')
    rqlexec('SET VC at_revision REV WHERE VC is VersionContent, '
            'REV eid %(rev)s, VC at_revision PREV, '
            'REV parent_revision PREV, '
            'NOT EXISTS(VC2 from_revision REV, VC content_for VF, '
            'VC2 content_for VF)',
            {'rev': reid}, 'rev')


class VCSConnectionWrapper(ConnectionWrapper):
    def __init__(self, source=None):
        ConnectionWrapper.__init__(self, source)
        self.vcs_transactions = {}

    def commit(self):
        # XXX move to a precommmit operation?
        for transaction in self.vcs_transactions.itervalues():
            transaction.commit()
        self.vcs_transactions.clear()
        ConnectionWrapper.commit(self)

    def rollback(self):
        # XXX move to a precommmit operation?
        for transaction in self.vcs_transactions.itervalues():
            transaction.rollback()
        self.vcs_transactions.clear()
        ConnectionWrapper.rollback(self)


class VCSSQLGenerator(SQLGenerator):

    def _visit_attribute_relation(self, relation):
        if relation.r_type == 'data':
            raise QueryError('querying data attribute of a versioned content '
                             'is not supported')
        return super(VCSSQLGenerator, self)._visit_attribute_relation(relation)

    def _linked_var_sql(self, variable, contextrels=None):
        rel = (contextrels and contextrels.get(variable.name) or
               variable.stinfo.get('principal') or
               iter(variable.stinfo['rhsrelations']).next())
        linkedvar = rel.children[0].variable
        linkedvar.accept(self)
        if rel.r_type == 'data':
            sql = 'VERSION_DATA(%s)' % linkedvar._q_sql
        else:
            sql = '%s.%s%s' % (linkedvar._q_sqltable, SQL_PREFIX, rel.r_type)
        return sql


class VCSSource(SQLiteAbstractSource):
    """VCS repository source"""
    sqlgen_class = VCSSQLGenerator

    support_entities = {'DeletedVersionContent': True,
                        'VersionContent': True,
                        'VersionedFile': True,
                        'Revision': True,}
    support_relations = {'content_for': True,
                         'from_revision': True,
                         'parent_revision': True,
                         'at_revision': True,
                         'vc_copy': True,
                         'vc_rename': True}

    options = SQLiteAbstractSource.options + (
        ('check-revision-interval',
         {'type' : 'int',
          'default': 5*60,
          'help': 'interval between checking of new revisions in repositories \
(default to 5 minutes).',
          'inputlevel': 2,
          }),
        ('rebuild-mode',
         {'type' : 'choice', 'choices': ('keep-eids', 'erase-all'),
          'default': 'erase-all',
          'help': 'tell how to reimport content when the sqlite database file \
isn\'t found. "erase-all" means delete all information about entities from \
this source and reimport everything. "keep-eids" will reimport vcs content \
trying to keep already affected eid, so relations you may have set won\'t get \
lost in the process. When using this value, take care that reimported content \
is a superset of what had been imported previously, else you may end in a \
corrupted database. Use "cubicweb-ctl db-check" in such cases.',
          'inputlevel': 2,
          }),
    )

    def __init__(self, repo, appschema, source_config, *args, **kwargs):
        SQLiteAbstractSource.__init__(self, repo, appschema, source_config,
                                      *args, **kwargs)
        self.check_interval = int(source_config.get('check-revision-interval',
                                                    5*60))
        self.rebuild_mode = source_config.get('rebuild-mode', 'erase-all')
        assert self.rebuild_mode in ('keep-eids', 'erase-all')
        self._recreate_entities = False
        # cache map repository's eid -> repository's path
        self.repo_eid_path = {}

    def get_connection(self):
        return VCSConnectionWrapper(self)

    @property
    def _sqlcnx(self):
        cnx = super(VCSSource, self)._sqlcnx
        # since actual data is not stored in the helper db, use this custom
        # registered procedure to easily extract it when needed
        def version_data(eid, source=self):
            """return file content for a given path / revision"""
            try:
                rev, repoeid, path = source.eid2extid(eid).split(':', 2)
                try:
                    repohdlr = source.repo_eid_path[typed_eid(repoeid)]
                except KeyError:
                    print 'key', repoeid, 'was not in cache'
                    self.import_content()
                    repohdlr = source.repo_eid_path[typed_eid(repoeid)]
                if repohdlr.encoding != 'utf-8':
                    path = unicode(path, 'utf-8').encode(repohdlr.encoding)
                res = repohdlr.file_content(path, int(rev))
            except:
                import traceback
                traceback.print_exc()
                raise
            # buffer is self.sqladapter.binary
            return buffer(res.getvalue())
        cnx.create_function("VERSION_DATA", 1, version_data)
        return cnx

    def init(self):
        """method called by the repository once ready to handle request"""
        if self._need_full_import:
            session = self.repo.internal_session()
            # fti / entities tables cleanup
            if self.rebuild_mode == 'keep-eids':
                self._recreate_entities = True
            else:
                self.cleanup_entities_info(session)
                self._recreate_entities = False
            session.execute('SET X latest_known_revision 0 WHERE X is Repository')
            session.commit()
            session.close()
            self._need_full_import = False
        # import content first, to avoid blocking on our sqlite connection once
        # the server is started. Startup may be slowed down but users won't wait
        # for request (potentially enough for http time out) and complain
        self.import_content()
        self._recreate_entities = False
        # register a task to check for new revisions
        self.repo.looping_task(self.check_interval, self.import_content)

    def repository_handler(self, repoent):
        try:
            repohdlr = VCS_REPOS[repoent.type](repoent.eid, repoent.path,
                                               repoent.encoding)
        except KeyError:
            msg = repoent.req._('%s is not a known repository type')
            raise ValidationError(repoent.eid, {'type': msg % repoent.type})
        except ImportError:
            msg = repoent.req._('missing python bindings to support %s repositories')
            raise ValidationError(repoent.eid, {'type': msg % repoent.type})
        self.repo_eid_path[repoent.eid] = repohdlr
        return repohdlr

    def import_content(self):
        session = self.repo.internal_session()
        try:
            for repoentity in session.execute(
                'Any X, T, P, SP, E, LR '
                'WHERE X is Repository, X type T, X path P, X subpath SP,'
                'X encoding E, X latest_known_revision LR').entities():
                repohdlr = self.repository_handler(repoentity)
                repohdlr.import_content(self, repoentity)
            session.commit()
        finally:
            session.close()

    ETYPE_EXTID_STR = {
        'VersionedFile': '%(repoeid)s:%(path)s',
        'Revision': '%(revision)s:%(repoeid)s',
        'VersionContent': '%(revision)s:%(repoeid)s:%(path)s',
        'DeletedVersionContent': '%(revision)s:%(repoeid)s:%(path)s',
        }

    def fdata2eid(self, fdata, etype, session):
        self._current_fdata = fdata
        extid = self.ETYPE_EXTID_STR[etype] % fdata
        return self.extid2eid(extid.encode('utf-8'), etype, session,
                              recreate=self._recreate_entities)

    def add_versioned_file(self, session, fdata):
        eid = self.fdata2eid(fdata, 'VersionedFile', session)
        self.add_version_content(session, fdata)
        return eid

    def add_revision(self, session, fdata):
        return self.fdata2eid(fdata, 'Revision', session)

    def add_version_content(self, session, fdata):
        return self.fdata2eid(fdata, 'VersionContent', session)

    def add_deleted_version_content(self, session, fdata):
        return self.fdata2eid(fdata, 'DeletedVersionContent', session)

    def before_entity_insertion(self, session, lid, etype, eid):
        """called by the repository when an eid has been attributed for an
        entity stored here but the entity has not been inserted in the system
        table yet.

        This method must return the an Entity instance representation of this
        entity.
        """
        entity = super(VCSSource, self).before_entity_insertion(session, lid,
                                                                etype, eid)
        fdata = self._current_fdata
        # complete entity for full text indexing and later insertion in our
        # helper database
        entity['creation_date'] = entity['modification_date'] = fdata['date']
        if etype == 'VersionedFile':
            entity['directory'], entity['name'] = split(fdata['path'])
            entity['from_repository'] = typed_eid(lid.split(':', 1)[0])
        elif etype == 'Revision':
            entity['from_repository'] = typed_eid(lid.split(':', 1)[1])
            for attr in ('revision', 'author', 'description', 'changeset',
                         'branch', 'parent_revision'):
                entity[attr] = fdata.get(attr)
        else:
            # etype in ('DeletedVersionContent', 'VersionContent')
            vfile = self.fdata2eid(fdata, 'VersionedFile', session)
            revision = self.fdata2eid(fdata, 'Revision', session)
            entity['content_for'] = vfile
            entity['from_revision'] = revision
            if etype == 'VersionContent':
                # done in a hook but doing it here as well avoid an additional
                # query to lookup filename
                entity['data'] = fdata['data']
                rencoding = self.repo_eid_path[fdata['repoeid']].encoding
                mt, enc = guess_mimetype_and_encoding(data=fdata['data'],
                                                      filename=fdata['path'],
                                                      fallbackencoding=rencoding)
                entity['data_format'] = mt
                entity['data_encoding'] = enc
                for inlinerel in ('vc_copy', 'vc_rename'):
                    if inlinerel in fdata:
                        entity[inlinerel] = fdata[inlinerel]
        return entity

    def after_entity_insertion(self, session, lid, entity):
        """called by the repository after an entity stored here has been
        inserted in the system table.
        """
        super(VCSSource, self).after_entity_insertion(session, lid, entity)
        # insert the entity into our helper database
        entity.pop('data', None)
        sqlcursor = session.pool[self.uri]
        insertlater = []
        for rtype in self.support_relations:
            if not self.schema.rschema(rtype).inlined:
                try:
                    eidtos = entity.pop(rtype)
                except KeyError:
                    continue
                if eidtos is None:
                    continue
                if not isinstance(eidtos, (list, tuple)):
                    eidtos = (eidtos,)
                insertlater.append((rtype, eidtos))
        # first pop repository if specified (eg VersionedFile entity)
        repository = entity.pop('from_repository', None)
        attrs = self.sqladapter.preprocess_entity(entity)
        sql = self.sqladapter.sqlgen.insert(SQL_PREFIX + str(entity.e_schema), attrs)
        self.doexec(sqlcursor, sql, attrs)
        if repository is not None and not hasattr(entity, '_cw_recreating'):
            session.execute('SET X from_repository Y WHERE X eid %(x)s, Y eid %(y)s',
                            {'x': entity.eid, 'y': repository})
        for rtype, eidtos in insertlater:
            for eidto in eidtos:
                session.repo.glob_add_relation(session,
                                               entity.eid, rtype, eidto)

    def revision_imported(self, session, fdata):
        """hooks called by repository backend when a revision has been fully
        imported to get a chance to handle correctly the at_revision relation
        """
        reid = self.fdata2eid(fdata, 'Revision', session)
        set_at_revision(session, reid)

    def _create_revision(self, session, entity):
        try:
            repoeid = entity.querier_pending_relations[('from_repository', 'subject')]
        except KeyError:
            repoeid = session.transaction_data.pop('vcsrepoeid', None)
            if repoeid is None:
                raise QueryError("the from_repository relation should be specified")
        revision = entity.get('revision', 0)
        if revision > 0: # set to 0 by hook
            raise QueryError("can't specify revision")
        cnx = session.pool.connection(self.uri)
        # should not have multiple transaction on the same repository
        if repoeid in cnx.vcs_transactions:
            raise QueryError('already processing a new revision')
        repohdlr = self.repo_eid_path[repoeid]
        transaction = repohdlr.revision_transaction(session, entity)
        transaction.reveid = entity.eid
        cnx.vcs_transactions[repoeid] = transaction
        entity['revision'] = transaction.rev
        entity.__extid = '%s:%s' % (transaction.rev, repoeid)

    def _create_version_content(self, session, entity):
        try:
            vfeid = entity['content_for']
            # data not stored in the local database, pop it
            data = entity.pop('data')
        except KeyError, ex:
            # missing data
            raise QueryError("missing necessary %s attribute" % ex)
        # retrieve associated VersionedFile instance
        vf = session.execute('Any X,D,N,R WHERE X name N, X directory D,'
                             'X from_repository R, X eid %(x)s',
                             {'x': vfeid}, 'x').get_entity(0, 0)
        repoeid = vf.repository.eid
        cnx = session.pool.connection(self.uri)
        try:
            transaction = cnx.vcs_transactions[repoeid]
        except KeyError:
            raise QueryError('you must create a Revision instance before '
                             'adding some content')
        repohdlr = self.repo_eid_path[repoeid]
        fname = repohdlr.add_versioned_file_content(session, transaction,
                                                    vf, entity, data)
        entity.__extid = '%s:%s:%s' % (transaction.rev, repoeid,
                                       fname.encode('utf-8'))
        return data

    def _create_deleted_version_content(self, session, entity):
        try:
            vfeid = entity['content_for']
        except KeyError, ex:
            # missing data
            raise QueryError("missing necessary %s attribute" % ex)
        # retrieve associated VersionedFile instance
        vf = session.execute('Any X,D,N,R WHERE X name N, X directory D,'
                             'X from_repository R, X eid %(x)s',
                             {'x': vfeid}, 'x').get_entity(0, 0)
        repoeid = vf.repository.eid
        cnx = session.pool.connection(self.uri)
        try:
            transaction = cnx.vcs_transactions[repoeid]
        except KeyError:
            raise QueryError('you must create a Revision instance before '
                             'adding some content')
        repohdlr = self.repo_eid_path[repoeid]
        fname = repohdlr.add_versioned_file_deleted_content(session, transaction,
                                                            vf, entity)
        entity.__extid = '%s:%s:%s' % (transaction.rev, repoeid,
                                       fname.encode('utf-8'))


    def _create_versioned_file(self, session, entity):
        try:
            repoeid = entity.querier_pending_relations[('from_repository', 'subject')]
        except KeyError:
            raise QueryError("the from_repository relation should be specified")
        fname = join(entity.directory, entity.name)
        entity.__extid = '%s:%s' % (repoeid, fname.encode('utf-8'))

    def add_entity(self, session, entity):
        """add a new entity to the source"""
        if entity.e_schema == 'Revision':
            self._create_revision(session, entity)
        elif entity.e_schema == 'VersionContent':
            data = self._create_version_content(session, entity)
        elif entity.e_schema == 'DeletedVersionContent':
            self._create_deleted_version_content(session, entity)
        elif entity.e_schema == 'VersionedFile':
            self._create_versioned_file(session, entity)
        else:
            raise NotImplementedError()
        # insert into the local database
        self.local_add_entity(session, entity)
        if entity.e_schema == 'VersionContent':
            # restore data for the text index
            entity['data'] = data

    IMMUTABLE_ATTRIBUTES = frozenset(('VersionedFile.directory', 'VersionedFile.name',
                                      'Revision.revision', 'Revision.changeset', 'Revision.branch',
                                      'DeletedVersionContent.from_revision', 'DeletedVersionContent.content_for',
                                      'VersionContent.from_revision', 'VersionContent.content_for', 'VersionContent.data',
                                      ))
    def update_entity(self, session, entity):
        for attr in entity.keys():
            if attr == 'eid':
                continue
            if '%s.%s' % (entity.id, attr) in self.IMMUTABLE_ATTRIBUTES:
                raise QueryError('%s attribute is not editable' % attr)
            # case where [Deleted]VersionContent is added using the web ui
            # and from_revision is added after its creation
            if attr == 'from_revision' and entity.eid in session.transaction_data.get('neweids', ()):
                continue
        self.local_update_entity(session, entity)

    def add_relation(self, session, subject, rtype, object):
        return self.local_add_relation(session, subject, rtype, object)

    def get_extid(self, entity):
        return entity.__extid # set by add_entity

VCSSource.set_nonsystem_types()

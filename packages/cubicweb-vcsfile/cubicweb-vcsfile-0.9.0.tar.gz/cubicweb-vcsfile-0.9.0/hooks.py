# -*- coding: utf-8 -*-
"""hooks for vcsfile content types

:organization: Logilab
:copyright: 2007-2009 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
"""
__docformat__ = "restructuredtext en"

import os

from logilab.mtconverter import guess_mimetype_and_encoding

from cubicweb import QueryError
from cubicweb.server.hooksmanager import Hook
from cubicweb.server.pool import PreCommitOperation, Operation

from cubes.vcsfile.repo import VCSException
from cubes.vcsfile.vcssource import get_vcs_source, set_at_revision


class AddRepositoryHook(Hook):
    """add repository eid to vcs source cache"""
    events = ('before_add_entity', )
    accepts = ('Repository',)

    def call(self, session, entity):
        source = get_vcs_source(session.repo)
        try:
            # check and register the repository into the source
            source.repository_handler(entity)
        except VCSException, ex:
            raise ex.to_validation_error(session._)


class AddVersionedFileHook(Hook):
    """classifies VersionedFile automatically according to their path in the
    repository (require cubicweb-tag and/or cubicweb-folder installed)
    """
    events = ('before_add_entity', )
    accepts = ('VersionedFile',)

    def call(self, session, entity):
        if hasattr(entity, '_cw_recreating'):
            return
        try:
            rschema = self.schema['tags']
            support_tags = rschema.has_rdef('Tag', entity.e_schema)
        except KeyError:
            support_tags = False
        try:
            rschema = self.schema['filed_under']
            support_folders = rschema.has_rdef(entity.e_schema, 'Folder')
        except KeyError:
            support_folders = False
        if not (support_tags or support_folders):
            return
        for directory in entity.directory.split(os.sep):
            if not directory:
                continue
            if support_tags:
                rset = session.execute('Tag X WHERE X name %(name)s',
                                       {'name': directory})
                if rset:
                    session.execute('SET T tags X WHERE X eid %(x)s, T eid %(t)s',
                                    {'x': entity.eid, 't': rset[0][0]}, 'x')
            if support_folders:
                rset = session.execute('Folder X WHERE X name %(name)s',
                                       {'name': directory})
                if rset:
                    session.execute('SET X filed_under F WHERE X eid %(x)s, F eid %(f)s',
                                    {'x': entity.eid, 'f': rset[0][0]}, 'x')

class AddVersionContentHook(Hook):
    events = ('before_add_entity',)
    accepts = ('VersionContent',)

    def call(self, session, entity):
        if not 'data_format' in entity or not 'data_encoding' in entity:
            try:
                vfeid = entity['content_for']
                data = entity['data']
            except KeyError, ex:
                raise QueryError('missing necessary "%s" value' % ex)
            repoeid, filename = session.execute(
                'Any R, FN WHERE X name FN, X eid %(x)s, X from_repository R',
                {'x': vfeid}, 'x')[0]
            repoencoding = get_vcs_source(session.repo).repo_eid_path[repoeid].encoding
            mt, enc = guess_mimetype_and_encoding(data=data, filename=filename,
                                                  fallbackencoding=repoencoding)
            if not 'data_format' in entity:
                entity['data_format'] = mt and unicode(mt)
            if not 'data_encoding' in entity:
                entity['data_encoding'] = enc and unicode(enc)
        if not session.is_internal_session:
            CheckRevisionOp(session, entity=entity)


class CheckRevisionOp(PreCommitOperation):

    def precommit_event(self):
        vc = self.entity
        revision = vc.from_revision[0]
        repository = revision.from_repository[0]
        source = get_vcs_source(self.session.repo)
        cnx = self.session.pool.connection(source.uri)
        try:
            transaction = cnx.vcs_transactions[repository.eid]
        except KeyError:
            raise QueryError('no transaction in progress for repository %s'
                             % repository.eid)
        if not transaction.reveid == revision.eid:
            raise QueryError('entity linked to a bad revision')


class AddRevisionContentHook(Hook):
    events = ('before_add_entity', )
    accepts = ('Revision',)
    def call(self, session, entity):
        if not entity.get('revision'):
            # new revision to be created, set a temporary value
            entity['revision'] = 0


# at_revision relation handling

class SetRevisionStateHook(Hook):
    events = ('after_add_entity',)
    accepts = ('Revision',)
    def call(self, session, entity):
        SetRevisionStateOperation(session, reid=entity.eid)


class SetRevisionStateOperation(PreCommitOperation):

    def precommit_event(self):
        if self.session.is_internal_session:
            return
        set_at_revision(self.session, self.reid)

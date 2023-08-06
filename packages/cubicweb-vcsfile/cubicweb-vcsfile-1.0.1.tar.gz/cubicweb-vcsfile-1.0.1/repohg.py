"""repository abstraction for a mercurial repository

:organization: Logilab
:copyright: 2007-2009 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
"""
__docformat__ = "restructuredtext en"

from os.path import split
from datetime import datetime

from mercurial import hg, ui, revlog, context, util
from mercurial.node import nullid, short as short_hex

from cubicweb import Binary, QueryError

from cubes.vcsfile import repo, bridge

_DELETED = object()


def bw_nb_revisions(changelog):
    """return the number of revisions in a repository's changelog,
    assuring mercurial < 1.1 compatibility
    """
    try:
        return len(changelog)
    except AttributeError: # hg < 1.1
        return changelog.count()


class HGRepository(repo.VCSRepository):
    type = 'hg'

    def import_content(self, repoentity):
        """import content from the mercurial repository"""
        assert self.eid == repoentity.eid
        try:
            repo = self.hgrepo()
        except Exception, ex:
            self.error('Impossible to open repository %s (%s)', self, ex)
            return
        changelog = repo.changelog
        actualrev = bw_nb_revisions(changelog)
        session = repoentity.req
        execute = session.execute
        latestrev = repoentity.latest_known_revision
        if actualrev < latestrev:
            # striped repo
            # very minimal support, this won't work if local number of
            # revisions has changed due to the strip
            self.warning('strip detected ? latest known revision is %s, latest '
                         'repository revision is %s', latestrev, actualrev)
            execute('DELETE Revision X WHERE X revision >= %(rev)s',
                    {'rev': actualrev})
            repoentity.set_attributes(latest_known_revision=actualrev)
            return
        self.info('hg repo %s: known revisions up to %s, repo revision %s',
                  repoentity.path, latestrev, actualrev)
        path_filter = repoentity.subpath
        for i in xrange(latestrev, actualrev):
            self.info('importing revision %s', i)
            node = changelog.node(i)
            ctx = repo.changectx(i)
            date = datetime.fromtimestamp(ctx.date()[0])
            #taglist = ctx.tags() #repo.nodetags(node)
            revdata = {'date': date, 'revision': i,
                       'author': unicode(ctx.user(), self.encoding, 'replace'),
                       'description': unicode(ctx.description(), self.encoding, 'replace'),
                       'changeset': unicode(short_hex(node)),
                       'branch': unicode(ctx.branch()),
                       }
            self.imported_revision = i # for hooks
            parents = [short_hex(n) for n in changelog.parents(node)
                       if n != nullid]
            if parents:
                if len(parents) == 1:
                    parents = execute('Revision X WHERE X changeset %(cs)s, '
                                      'X from_repository R, R eid %(r)s',
                                      {'cs': parents[0], 'r': self.eid})
                else:
                    parents = execute('Revision X WHERE X changeset IN (%s), '
                                      'X from_repository R, R eid %%(r)s'
                                      % ','.join("'%s'"%cs for cs in parents),
                                      {'r': self.eid})
            revdata['parents'] = [r[0] for r in parents]
            reveid = bridge.import_revision(session, self.eid, **revdata)
            changes = repo.status(ctx.parents()[0].node(), ctx.node())[:5]
            modified, added, removed, deleted, unknown = changes
            for path in modified + added:
                upath = unicode(path, self.encoding, 'replace')
                if not (path_filter is None or upath.startswith(path_filter)):
                    continue
                vcdata = {}
                filectx = ctx[path]
                renameinfo = filectx.renamed()
                if renameinfo:
                    oldfile, fileid = renameinfo
                    pfctx = repo.filectx(oldfile, fileid=fileid)
                    pcs = short_hex(pfctx.node())
                    dir, name = split(unicode(oldfile, self.encoding, 'replace'))
                    pvc = execute('VersionContent X WHERE '
                                  'X from_revision REV, REV changeset %(cs)s, '
                                  'REV from_repository R, R eid %(r)s, '
                                  'X content_for VF, VF directory %(dir)s, VF name %(name)s',
                                  {'cs':  pcs, 'r': self.eid,
                                   'dir': dir, 'name': name})
                    if pvc:
                        assert len(pvc) == 1
                        if oldfile in removed:
                            vcdata['vc_rename'] = pvc[0][0]
                        else:
                            vcdata['vc_copy'] = pvc[0][0]
                    else:
                        self.error('detected copy or rename of %s@%s but unable'
                                   ' to find associated version content',
                                   oldfile, pcs)
                bridge.import_version_content(session, self.eid, reveid, upath,
                                              date, **vcdata)
            for path in removed + deleted:
                upath = unicode(path, self.encoding, 'replace')
                if not (path_filter is None or upath.startswith(path_filter)):
                    continue
                bridge.import_deleted_version_content(session, self.eid, reveid,
                                                      upath, date)
            bridge.set_at_revision(session, reveid)
        if actualrev > latestrev:
            repoentity.set_attributes(latest_known_revision=actualrev)

    def hgrepo(self):
        return hg.repository(ui.ui(), self.path)

    def _file_content(self, path, rev):
        """extract a binary string with the content of the file at `path` for
        revision `rev` in the repository
        """
        ctx = self.hgrepo().changectx(rev)
        return ctx[path].data()

    def revision_transaction(self, session, entity):
        """open a transaction to create a new revision corresponding to the
        given entity
        """
        return HGTransaction(self, session, entity)

    def add_versioned_file_content(self, session, transaction, vf, entity,
                                   data):
        """add a new revision of a versioned file"""
        vfpath = self.encode(vf.path)
        transaction.changes[vfpath] = context.memfilectx(
            vfpath, data.getvalue(), islink=False, isexec=False, copied=None)
        return vf.path

    def add_versioned_file_deleted_content(self, session, transaction, vf,
                                           entity):
        """add a new revision of a just deleted versioned file"""
        transaction.changes[self.encode(vf.path)] = _DELETED
        return vf.path


class HGTransaction(object):
    def __init__(self, repohdlr, session, revision):
        self.repohdlr = repohdlr
        self.session = session
        self.revision = revision
        self.repo = repohdlr.hgrepo()
        self._wlock = self.repo.wlock()
        self._lock = self.repo.lock()
        self.extra = {}
        self.changes = {}

    @property
    def rev(self):
        """newly created revision number"""
        return bw_nb_revisions(self.repo.changelog)

    def _filectx(self, repo, memctx, path):
        """callable receiving the repository, the current memctx object and the
        normalized path of requested file, relative to repository root. It is
        fired by the commit function for every file in 'files', but calls order
        is undefined. If the file is available in the revision being committed
        (updated or added), filectxfn returns a memfilectx object. If the file
        was removed, filectxfn raises an IOError. Moved files are represented by
        marking the source file removed and the new file added with copy
        information (see memfilectx).
        """
        if self.changes[path] is _DELETED:
            raise IOError()
        return self.changes[path]

    def commit(self):
        if not self.changes:
            raise QueryError('nothing changed')
        # XXX merging branches
        encode = self.repohdlr.encode
        branch = encode(self.revision.get('branch') or u'default')
        if branch != u'default':
            self.extra['branch'] = branch
        author = encode(self.revision.get('author', u''))
        msg = encode(self.revision.get('description', u''))
        try:
            p1 = self.repo.branchtags()[branch]
        except KeyError:
            # new branch
            p1 = self.repo.branchtags()['default']
        p2 = None
        # ensure mercurial will use configured repo encoding, not locale's
        # encoding
        # XXX modifying module's global is not very nice but I've no other idea
        util._encoding = self.repohdlr.encoding
        ctx = context.memctx(self.repo, (p1, p2), msg, self.changes.keys(),
                             self._filectx, author, extra=self.extra)
        node = self.repo._commitctx(ctx, force=True, force_editor=False,
                                    empty_ok=True, use_dirstate=False,
                                    update_dirstate=False)
        # update revision's record to set correct changeset
        #
        # take care, self.repo != self.session.repo (eg mercurial repo instance
        # / rql repository)
        source = self.session.repo.system_source
         # remove previous cached value to only save the changeset
        self.revision.clear()
        self.revision['eid'] = self.revision.eid
        self.revision['changeset'] = unicode(short_hex(node))
        source.update_entity(self.session, self.revision)
        # XXX restore entity's dict?
        self.rollback()

    def rollback(self):
        del self._wlock
        del self._lock

from logging import getLogger
from cubicweb import set_log_methods
set_log_methods(HGRepository, getLogger('cubicweb.sources.hg'))

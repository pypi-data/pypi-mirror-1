"""repository abstraction for a mercurial repository

:organization: Logilab
:copyright: 2007-2009 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
"""
__docformat__ = "restructuredtext en"

from datetime import datetime
from os.path import split

from mercurial import hg, ui, revlog, context, util
from mercurial.node import nullid, short as short_hex

from cubicweb import Binary, QueryError
from cubicweb.server.sqlutils import SQL_PREFIX

from cubes.vcsfile.repo import VCSRepository
from cubes.vcsfile.vcssource import get_vcs_source


def bw_nb_revisions(changelog):
    """return the number of revisions in a repository's changelog,
    assuring pre mercurial 1.1 compatibility
    """
    try:
        return changelog.count()
    except AttributeError: # hg >= 1.1
        return len(changelog)

class HGRepository(VCSRepository):
    type = 'hg'

    def import_content(self, source, repoentity):
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
        path_filter = repoentity.subpath
        for i in xrange(latestrev, actualrev):
            node = changelog.node(i)
            changeset = short_hex(node)
            ctx = repo.changectx(i)
            date = datetime.fromtimestamp(ctx.date()[0])#date[0])
            author = unicode(ctx.user(), self.encoding, 'replace')
            msg = unicode(ctx.description(), self.encoding, 'replace')
            #taglist = ctx.tags() #repo.nodetags(node)
            fdata = {'author': author, 'date': date, 'description': msg,
                     'changeset': changeset, 'branch': ctx.branch(),
                     'revision': i, 'repoeid': self.eid}
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
            if parents: # retest in case parent revision(s) has not been found
                fdata['parent_revision'] = [r[0] for r in parents]
            changes = repo.status(ctx.parents()[0].node(), ctx.node())[:5]
            modified, added, removed, deleted, unknown = changes
            imported = False
            for path in modified + added:
                upath = unicode(path, self.encoding, 'replace')
                if not (path_filter is None or upath.startswith(path_filter)):
                    continue
                fdata['path'] = upath
                filectx = ctx[path]
                fdata['data'] = Binary(filectx.data())
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
                            fdata['vc_rename'] = pvc[0][0]
                        else:
                            fdata['vc_copy'] = pvc[0][0]
                    else:
                        self.error('detected copy or rename of %s@%s but unable'
                                   ' to find associated version content',
                                   oldfile, pcs)
                source.add_version_content(session, fdata)
                imported = True
            for path in removed + deleted:
                upath = unicode(path, self.encoding, 'replace')
                if not (path_filter is None or upath.startswith(path_filter)):
                    continue
                fdata['path'] = upath
                source.add_deleted_version_content(session, fdata)
                imported = True
            if imported:
                source.revision_imported(session, fdata)
        if actualrev > latestrev:
            repoentity.set_attributes(latest_known_revision=actualrev)

    def hgrepo(self):
        return hg.repository(ui.ui(), self.path)

    def file_content(self, path, rev):
        """extract a binary stream with the content of the file at `path` at
        revision `rev` in the repository
        """
        assert isinstance(path, str)
        ctx = self.hgrepo().changectx(rev)
        return Binary(ctx[path].data())

    def revision_transaction(self, session, entity):
        """open a transaction to create a new revision corresponding to the
        given entity
        """
        return HGTransaction(self, session, entity)

    def add_versioned_file_content(self, session, transaction, vf, entity, data):
        """add a new revision of a versioned file"""
        vfpath = self.encode(vf.path)
        transaction.changes[vfpath] = context.memfilectx(vfpath, data.getvalue(),
                                                         islink=False, isexec=False,
                                                         copied=None)
        return vf.path

    def add_versioned_file_deleted_content(self, session, transaction, vf, entity):
        """add a new revision of a just deleted versioned file"""
        transaction.changes[self.encode(vf.path)] = _DELETED
        return vf.path

_DELETED = object()

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
        # XXX merging, new branches
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
        # take care, self.repo != self.session.repo (eg mercurial repo instance
        # / rql repository)
        source = get_vcs_source(self.session.repo)
        source.local_update_entity(self.session, self.revision,
                                   {SQL_PREFIX + 'eid': self.revision.eid,
                                    SQL_PREFIX + 'changeset': unicode(short_hex(node))})
        self.rollback()

    def rollback(self):
        del self._wlock
        del self._lock

from logging import getLogger
from cubicweb import set_log_methods
set_log_methods(HGRepository, getLogger('cubicweb.sources.hg'))

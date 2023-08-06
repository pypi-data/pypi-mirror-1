"""repository abstraction for a subversion repository

:organization: Logilab
:copyright: 2007-2009 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
"""
__docformat__ = "restructuredtext en"

import traceback
from os.path import join, sep, split
from datetime import datetime

from logilab.common.decorators import cached

from svn import fs, repos, core, delta, ra

from cubicweb import Binary, QueryError

from cubes.vcsfile.repo import VCSRepository


def file_content(fsrep, path, rev):
    content = Binary()
    try:
        root = fs.revision_root(fsrep, rev)
        try:
            stream = fs.file_contents(root, path)
        except:
            return None
        while 1:
            data = core.svn_stream_read(stream, core.SVN_STREAM_CHUNK_SIZE)
            content.write(data)
            if len(data) < core.SVN_STREAM_CHUNK_SIZE:
                break
        core.svn_stream_close(stream)
    except:
        traceback.print_exc()
    return content


class SVNRepository(VCSRepository):
    type = 'svn'

    def __init__(self, *args, **kwargs):
        super(SVNRepository, self).__init__(*args, **kwargs)
        # svn uses utf-8 internally; we should not try to contradict that
        self.encoding = 'utf-8'

    def canonicalize(self, fspath):
        fspath = core.svn_path_canonicalize(fspath)
        repos.open(fspath) # throwaway, just check it's a valid svn repository
        return fspath

    def import_content(self, source, repoentity):
        """import content from the subversion repository

        NOTE: server side only method
        """
        try:
            repo = repos.open(self.path)
            fsrep = repos.fs(repo)
        except core.SubversionException, ex:
            self.error('Impossible to open repository %s (%s)', self, ex)
            return
        callbacks = ra.Callbacks()
        #ra_ctx = ra.open2('file://' + self.path, callbacks, None, None)
        latestrev = rev = repoentity.latest_known_revision
        actualrev = fs.youngest_rev(fsrep)
        session = repoentity.req
        while rev < actualrev:
            base_root = fs.revision_root(fsrep, rev)
            rev += 1
            self.info('importing content of %s for revision %s', self, rev)
            # the base of the comparison
            editor = SVNImporter(source, repoentity.eid, self.encoding, fsrep, #repo, ra_ctx,
                                 session, base_root, rev,
                                 repoentity.subpath)
            editor.import_revision()
        if actualrev > latestrev:
            repoentity.set_attributes(latest_known_revision=actualrev)

    def file_content(self, path, rev):
        """extract a binary stream with the content of the file at `path` at
        revision `rev` in the repository
        """
        fsrep = repos.fs(repos.open(self.path))
        assert isinstance(path, str)
        return file_content(fsrep, path, rev)

    def revision_transaction(self, session, entity):
        """open a transaction to create a new revision corresponding to the
        given entity
        """
        if session.transaction_data.get('%s_info' % self.eid):
            repoptr, fsrep = session.transaction_data.get('%s_info' % self.eid)
        else:
            repoptr = repos.open(self.path)
            fsrep = repos.fs(repoptr)
            session.transaction_data['%s_info' % self.eid] = (repoptr, fsrep)
        # open a transaction against HEAD
        return SVNTransaction(repoptr, fsrep,
                              self.encode(entity.get('author', u'')),
                              self.encode(entity.get('description', u'')))

    def add_versioned_file_content(self, session, transaction, vf, entity, data):
        """add a new revision of a versioned file"""
        root = transaction.root
        # check if the parent directory exists in the repository
        directory = vf.directory.encode(self.encoding)
        if directory:
            parts = directory.split(sep)
            for i in xrange(len(parts)):
                directory = sep.join(parts[:i+1])
                kind = fs.check_path(root, directory)
                if kind == core.svn_node_none:
                    fs.make_dir(root, directory)
        # check if the file exists in the repository
        fname = join(directory, vf.name.encode(self.encoding))
        kind = fs.check_path(root, fname)
        if kind == core.svn_node_none:
            self.info('file %r does not exist in repo %s, creating...',
                      fname, self)
            fs.make_file(root, fname)
        else:
            self.info('updating file %r in repo %s', fname, self)
        handler, baton = fs.apply_textdelta(root, fname, None, None)
        delta.svn_txdelta_send_string(data.getvalue(), handler, baton)
        transaction.modified.add(fname)
        return fname.decode(self.encoding)

    def add_versioned_file_deleted_content(self, session, transaction, vf, entity):
        """add a new revision of a just deleted versioned file"""
        root = transaction.root
        # check if the file exists in the repository
        directory = vf.directory.encode(self.encoding)
        fname = join(directory, vf.name.encode(self.encoding))
        kind = fs.check_path(root, fname)
        if kind == core.svn_node_none:
            self.debug('file %r does not exist in repo %s',
                      fname, self)
            raise Exception('file %r does not exist' % fname)
        self.info('deleting %r from repo', fname)
        fs.delete(root, fname)
        transaction.modified.add(fname)
        return fname.decode(self.encoding)


class SVNTransaction(object):
    def __init__(self, repoptr, fsrep, author, msg):
        self.modified = set()
        rev = fs.youngest_rev(fsrep)
        txn = repos.fs_begin_txn_for_commit(repoptr, rev, author, msg)
        root = fs.txn_root(txn)
        #rev_root = fs.revision_root(fsrep, rev)
        self.root = root
        self.rev = rev+1
        self.txn = txn
        self.repoptr = repoptr

    def commit(self):
        if not self.modified:
            raise QueryError('nothing changed')
        repos.fs_commit_txn(self.repoptr, self.txn)

    def rollback(self):
        fs.abort_txn(self.txn)


class SVNImporter(delta.Editor):
    def __init__(self, source, repoeid, repoencoding, fsrep, #repo, ra_ctx,
                 session, base_root, rev, path_filter=None):
        self.source = source
        self.repoeid = repoeid
        self.encoding = repoencoding
        #self.svnrepo = repo
        self.fsrep = fsrep
        #self.ra_ctx = ra_ctx
        self.session = session
        self.base_root = base_root
        self.rev = rev
        self.root = fs.revision_root(fsrep, rev)
        if isinstance(path_filter, unicode):
            # if we don't encode we may get unicode error when comparing files'
            # path against the path filter
            path_filter = path_filter.encode(repoencoding)
        self.path_filter = path_filter
        self.execute = self.session.execute
        self.imported = False

    def import_revision(self):
        def authz_cb(root, path, pool):
            return 1
        # construct the editor
        e_ptr, e_baton = delta.make_editor(self)
        # compute the delta
        repos.dir_delta(self.base_root, '', '', self.root, '',
                        e_ptr, e_baton, authz_cb, 0, 1, 0, 0)
        if self.imported:
            self.source.revision_imported(self.session,
                                          {'repoeid': self.repoeid,
                                           'revision': self.rev})

    @cached
    def base_rev_content(self):
        fdata = {'repoeid': self.repoeid, 'revision': self.rev}
        author = fs.revision_prop(self.fsrep, self.rev,
                                  core.SVN_PROP_REVISION_AUTHOR)
        fdata['author'] = unicode(author, self.encoding, 'replace')
        rawdate = fs.revision_prop(self.fsrep, self.rev,
                                   core.SVN_PROP_REVISION_DATE)
        if rawdate:
            aprtime = core.svn_time_from_cstring(rawdate)
            # aprtime is microseconds; make seconds
            # assume secs in local TZ XXX we don't really know the TZ, do we?
            fdata['date'] = datetime.fromtimestamp(aprtime / 1000000)
        else:
            fdata['date'] = datetime.now()
        description = fs.revision_prop(self.fsrep, self.rev,
                                       core.SVN_PROP_REVISION_LOG)
        fdata['description'] = unicode(description, self.encoding,
                                       'replace')
        parent = self.execute('Revision X WHERE X revision %(rev)s, '
                              'X from_repository R, R eid %(r)s',
                              {'rev': self.rev - 1, 'r': self.repoeid})
        if parent: # retest in case parent revision(s) has not been found
            fdata['parent_revision'] = parent[0][0]
        self.imported = True
        return fdata

    def rev_content(self, path):
        fdata = self.base_rev_content()
        fdata['path'] = unicode(path, self.encoding, 'replace')
        fdata['data'] = file_content(self.fsrep, path, self.rev)
        # XXX code below may be used to get branches/tags information
        # note mergeinfo require svn >= 1.5 (an update of the repo backend may
        # be necessary)
##         print path, self.rev
##         print 'LOCS', ra.get_locations(self.ra_ctx, path, self.rev, range(1, self.rev))
##         print core.SVN_PROP_MERGEINFO, fs.node_prop(self.root, path, core.SVN_PROP_MERGEINFO)
##         try:
##             print 'FMI {',
##             minfos = repos.fs_get_mergeinfo(self.svnrepo, [path], self.rev,
##                                             core.svn_mergeinfo_inherited,
##                                             False, None, None)
##             for mf, mfinfos in minfos.iteritems():
##                 print mf, ': {',
##                 for mergedf, revranges in mfinfos.iteritems():
##                     print mergedf, [(rev.start, rev.end) for rev in revranges], ',',
##                 print '}',

##             print '}'
##         except core.SubversionException:
##             print 'not supported'
        return fdata

    def match_path(self, path):
        return self.path_filter is None or path.startswith(self.path_filter)

    # svn generated events ####################################################

    def open_root(self, base_revision, dir_pool):
        #print 'open_root', base_revision, dir_pool
        pass

    def change_dir_prop(self, dir_baton, name, value, pool):
        #print 'change_dir_prop', dir_baton, name, value, pool
        pass

    def open_directory(self, path, *args):
        #print 'open_directory', path
        pass

    def close_directory(self, baton):
        #print 'close_directory', baton
        pass

    def add_file(self, path, *args):
        #print 'add_file', path
        if self.match_path(path):
            fdata = self.rev_content(path)
            self.source.add_versioned_file(self.session, fdata)

    def add_directory(self, path, *args):
        #print 'add_directory', path
        pass

    def change_file_prop(self, file_baton, name, value, pool):
        #print 'change_file_prop', file_baton, name, value, pool
        pass

    def open_file(self, path, *args):
        #print 'open file', path
        if self.match_path(path):
            fdata = self.rev_content(path)
            self.source.add_version_content(self.session, fdata)

    def close_file(self, file_baton, text_checksum):
        pass

    def delete_entry(self, path, revision, parent_baton, pool):
        if self.match_path(path):
            # can't use svn property, return svn_core_none for deleted items
            fdata = self.base_rev_content()
            directory, name = split(path)
            if self.execute(
                'Any X WHERE X is VersionedFile, X directory %(path)s, '
                'X name %(name)s, X from_repository R, R eid %(r)s',
                {'path': directory, 'name': name, 'r': self.repoeid}):
                # deleted file
                fdata['path'] = unicode(path, self.encoding, 'replace')
                self.source.add_deleted_version_content(self.session, fdata)
                return
            # deleted directory
            for childdir, childname in self.execute(
                'Any XD, XN WHERE X is VersionedFile, X directory ~= %(path)s, '
                'X from_repository R, R eid %(r)s, X directory XD, X name XN',
                {'path': path + '%', 'r': self.repoeid}):
                fdata['path'] = join(childdir, childname)
                self.source.add_deleted_version_content(self.session, fdata)

    def apply_textdelta(self, file_baton, base_checksum):
        #print 'apply_textdelta', file_baton, base_checksum
        pass

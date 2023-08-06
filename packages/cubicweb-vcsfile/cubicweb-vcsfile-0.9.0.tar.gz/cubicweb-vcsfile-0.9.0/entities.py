"""entity classes for vcsfile content types


:organization: Logilab
:copyright: 2007-2009 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
"""
__docformat__ = "restructuredtext en"

from logilab.common.decorators import cached
from logilab.common.compat import any

from cubicweb import Binary
from cubicweb.interfaces import IPrevNext, IDownloadable
from cubicweb.entities import AnyEntity, fetch_config


def rql_revision_content(repoeid, revnum, branch=None):
    """return rql query to get the repository content at a given revision"""
    # XXX: MAX(V) is a trick necessary because RQL doesn't support subqueries,
    #      which would be necessary to have the correct query. This trick is ok
    #      since we know that entity with MAX(V) has MAX(VR) as well, due to
    #      source implementation
    args = {'rev': revnum, 'x': repoeid, 'branch': branch}
    return ('Any MAX(V),MAX(REV),F,D,N GROUPBY D,N,F ORDERBY D,N '
            'WHERE V content_for F, V from_revision VR, VR revision REV, '
            'VR branch %(branch)s, '
            'F directory D, F name N, F from_repository R, R eid %(x)s, '
            'F is VersionedFile, (VR revision <= %(rev)s AND NOT EXISTS('
            'X is DeletedVersionContent, X content_for F, X from_revision XR, '
            'XR branch %(branch)s, XR revision < %(rev)s, XR revision >= REV))'
            ), args

_MARKER = object()


class Repository(AnyEntity):
    """customized class for Repository entities"""
    id = 'Repository'
    fetch_attrs, fetch_order = fetch_config(['path', 'subpath', 'type'])

    def dc_title(self):
        title = '%s:%s' % (self.type, self.path)
        if self.subpath:
            title += ' (%s)' % self.subpath
        return title

    # navigation in versioned content #########################################

    def branches(self):
        return [b for b, in self.req.execute(
            'DISTINCT Any B WHERE R eid %(r)s, REV from_repository REPO, '
            'REV branch B', {'r' : self.eid}, 'r')]

    @cached
    def branch_head(self, branch=_MARKER):
        """return latest revision of the given branch
        """
        if branch is _MARKER:
            branch = self.default_branch()
        rset = self.req.execute(
            'Any MAX(REV) WHERE V at_revision REV, REV branch %(branch)s, '
            'REV from_repository R, R eid %(r)s',
            {'r': self.eid, 'branch': branch}, 'r')
        if rset[0][0] is None:
            return None
        return rset.get_entity(0, 0)

    def versioned_file(self, directory, filename):
        rset = self.req.execute(
            'Any X WHERE X is VersionedFile, X from_repository R, '
            'R eid %(repo)s, X directory %(dir)s, X name %(name)s',
            {'repo' : self.eid, 'dir' : directory, 'name' : filename})
        assert len(rset) == 1, rset
        return rset.get_entity(0, 0)

    def is_directory_deleted(self, directory):
        # XXX same MAX(X) trick as above
        rset = self.req.execute(
            'Any MAX(VC), MAX(REV) GROUPBY VF '
            'WHERE VC from_revision R, R revision REV, R from_repository X, '
            'X eid %(x)s, VC content_for VF, VF directory ~= %(dir)s',
            {'x': self.eid, 'dir': directory}, 'x')
        return not any(e for e in rset.entities() if e.id == 'VersionContent')

    # vcs write support ########################################################

    def default_branch(self):
        return {'subversion': None, 'mercurial': u'default'}[self.type]

    def make_revision(self, msg=None, author=_MARKER, branch=_MARKER):
        if branch is _MARKER:
            branch = self.default_branch()
        if author is _MARKER:
            author = self.req.user.login
        parent = self.branch_head(branch)
        assert parent
        rset = self.req.execute(
            'INSERT Revision R: R description %(desc)s, R author %(author)s, '
            'R branch %(branch)s, R from_repository X, R parent_revision PR '
            'WHERE X eid %(x)s, PR eid %(pr)s',
            {'desc' : msg, 'author': author, 'branch': branch,
             'x' : self.eid, 'pr': parent.eid}, ('x', 'pr'))
        return rset.get_entity(0, 0)

    def vcs_add(self, filedir, filename, stream, **kwargs):
        vf = self.req.execute(
            'INSERT VersionedFile X: X from_repository R, X directory %(dir)s, '
            'X name %(name)s WHERE R eid %(repo)s ',
            {'repo': self.eid, 'dir': filedir,
             'name': filename}).get_entity(0, 0)
        vf.vcs_upload_revision(stream, **kwargs)
        return vf.eid


class Revision(AnyEntity):
    """customized class for Revision entities"""
    id = 'Revision'
    fetch_attrs, fetch_order = fetch_config(['revision', 'changeset', 'author',
                                             'description', 'creation_date'])
    __implements__ = AnyEntity.__implements__ + (IPrevNext,)

    def dc_title(self):
        if self.changeset:
            return self.req._('revision #%s:%s') % (self.revision, self.changeset)
        else:
            return self.req._('revision #%s') % self.revision

    def dc_long_title(self):
        return self.req._('%(rev)s of repository %(repo)s') % {
            'rev': self.dc_title(), 'repo': self.repository.dc_title()}

    def previous_entity(self): # IPrevNext
        # may have multiple parents, take the first one in the same branch...
        rset = self.req.execute('Any X LIMIT 1 WHERE X parent_revision R , '
                                'R eid %(r)s, X branch %(branch)s',
                                {'r': self.eid, 'branch': self.branch})
        if rset:
            return rset.get_entity(0, 0)

    def next_entity(self): # IPrevNext
        # may have multiple children, take the first one in the same branch...
        rset = self.req.execute('Any X LIMIT 1 WHERE R parent_revision X , '
                                'R eid %(r)s, X branch %(branch)s',
                                {'r': self.eid, 'branch': self.branch})
        if rset:
            return rset.get_entity(0, 0)

    def parent(self): # for breadcrumbs
        return self.repository

    def add_related_schemas(self): # disable automatic add related actions
        return []

    def pre_web_edit(self):
        """callback called by the web editcontroller when an entity will be
        created/modified, to let a chance to do some entity specific stuff.
        """
        if not self.has_eid():
            try:
                repoeid = self.linked_to('from_repository', 'subject', remove=False)[0]
            except IndexError:
                raise RequestError('missing repository information')
            self.req.set_shared_data('vcsrepoeid', repoeid, querydata=True)

    # navigation in versioned content #########################################

    @property
    def repository(self):
        return self.from_repository[0]


class VersionedFile(AnyEntity):
    """customized class for VersionedFile entities"""
    id = 'VersionedFile'
    fetch_attrs, fetch_order = fetch_config(['directory', 'name'])

    # XXX branches
    def dc_title(self):
        if self.revision_deleted():
            return '%s (%s)' % (self.path, self.req._('DELETED'))
        return self.path

    def dc_long_title(self):
        return self.req._('%(path)s (from repository %(repotype)s:%(repo)s)') % {
            'path': self.dc_title(), 'repo': self.repository.path,
            'repotype': self.repository.type}

    def parent(self): # for breadcrumbs
        return self.repository

    def add_related_schemas(self): # disable automatic add related actions
        return []

    # navigation in versioned content #########################################

    @property
    def repository(self):
        return self.from_repository[0]

    @property
    def path(self):
        if self.directory:
            return '%s/%s' % (self.directory, self.name)
        return self.name

    @property
    def revisions(self):
        """return an ordered list of revision contents for this file"""
        return self.reverse_content_for

    @property
    def head(self):
        return self.branch_head()

    @cached
    def version_content(self, revnum):
        if revnum is None:
            return self.branch_head()
        rset = self.req.execute(
            'Any C WHERE C content_for VF, C from_revision R, '
            'R revision %(rnum)s, VF eid %(x)s',
            {'rnum' : revnum, 'x' : self.eid}, 'x')
        if rset:
            return rset.get_entity(0, 0)
        return None

    @cached
    def branch_head(self, branch=_MARKER):
        """return latest [deleted] version content for this file in the given
        branch
        """
        if branch is _MARKER:
            branch = self.repository.default_branch()
        rset = self.req.execute(
            'Any MAX(V) WHERE X eid %(x)s, V content_for X, V at_revision REV, '
            'REV branch %(branch)s',
            {'x': self.eid, 'branch': branch}, 'x')
        # content_for relation is not mandatory on VersionedFile entities
        if rset[0][0] is None:
            return None
        return rset.get_entity(0, 0)

    def deleted_in_branch(self, branch=_MARKER):
        """deleted in branch != does not even exist in branch
        """
        head = self.branch_head(branch)
        return head and not isinstance(self.branch_head(branch), VersionContent) or False

    def revision_deleted(self, revnum=None):
        return not isinstance(self.version_content(revnum), VersionContent)

    def revnum_author_msg_branch(self):
        """return an ordered list of

           (vcs revision number, author, commit message, branch)

        where this document has been modified
        """
        return self.req.execute(
            'DISTINCT Any RNUM, A, D, B ORDERBY RNUM, A, D, B '
            'WHERE C from_revision REV, REV revision RNUM, REV author A, '
            'REV branch B, REV description D, C content_for VF, VF eid %(x)s',
            {'x' : self.eid}, 'x')

    # vcs write support #######################################################

    def vcs_rm(self, rev=None, **kwargs):
        """either takes a rev or a kwargs having keys :
        branch, msg, author
        """
        if rev is None:
            if not 'msg' in kwargs:
                kwargs['msg'] = self.req._('deleted %s') % self.dc_title()
            rev = self.repository.make_revision(**kwargs)
        yet = self.req.execute('DeletedVersionContent D WHERE D content_for X, '
                               'X eid %(x)s', {'x' : self.eid}, 'x')
        if not len(yet):
            self.req.execute(
                'INSERT DeletedVersionContent D: D content_for X, '
                'D from_revision R WHERE X eid %(x)s, R eid %(r)s',
                {'x' : self.eid, 'r' : rev.eid}, ('x', 'r'))

    def vcs_upload_revision(self, stream, rev=None, **kwargs):
        """either takes a rev or a kwargs having keys :
        branch, msg, author
        """
        if rev is None:
            rev = self.repository.make_revision(**kwargs)
        return self.req.execute(
            'INSERT VersionContent X: '
            'X content_for VF, X from_revision REV, X data %(data)s '
            'WHERE VF eid %(vfeid)s, REV eid %(rev)s',
            {'vfeid' : self.eid, 'rev' : rev.eid,
             'data' : Binary(stream.read())})[0][0]


class DeletedVersionContent(AnyEntity):
    """customized class for DeletedVersionContent entities"""
    id = 'DeletedVersionContent'
    fetch_attrs, fetch_order = fetch_config(['from_revision', 'content_for'], order='DESC')
    __implements__ = AnyEntity.__implements__ + (IPrevNext,)

    def dc_title(self):
        return self.req._('%(file)s DELETED (revision %(revision)s)') % {
            'file': self.file.path, 'revision': self.rev.revision}

    def dc_long_title(self):
        rev = self.rev
        return self.req._('%(file)s DELETED (revision %(revision)s on %(date)s by %(author)s)') % {
            'file': self.file.path, 'revision': rev.revision,
            'author': rev.author, 'date': rev.printable_value('creation_date')}

    def dc_description(self, format='text/plain'):
        # override cubicweb's default implementation because it requires
        # 'description' to be a real schema attribute but it's only
        # a class property in our case
        return self.rev.dc_description(format)

    def previous_entity(self): # IPrevNext
        rset = self.req.execute('Any PV,R,PVR,VF ORDERBY PVR DESC LIMIT 1 '
                                'WHERE PV from_revision R, R revision PVR, '
                                'R branch %(b)s, PV content_for VF, '
                                'R revision < %(r)s, VF eid %(vf)s',
                                {'r': self.rev.revision, 'b': self.rev.branch,
                                 'vf': self.file.eid})
        if rset:
            return rset.get_entity(0, 0)

    def next_entity(self): # IPrevNext
        rset = self.req.execute('Any NV,R,NVR,VF ORDERBY NVR ASC LIMIT 1 '
                                'WHERE NV from_revision R, R revision NVR, '
                                'R branch %(b)s, NV content_for VF, '
                                'R revision > %(r)s, VF eid %(vf)s',
                                {'r': self.rev.revision, 'b': self.rev.branch,
                                 'vf': self.file.eid})
        if rset:
            return rset.get_entity(0, 0)

    def parent(self): # for breadcrumbs
        return self.file

    # navigation in versioned content #########################################

    @property
    def repository(self):
        return self.rev.repository

    @property
    def file(self):
        return self.content_for[0]

    @property
    def rev(self):
        return self.from_revision[0]

    @property
    def head(self):
        return self.file.head

    def is_head(self, branch=_MARKER):
        return self.eid == self.file.branch_head(branch).eid

    # < 0.7 bw compat properties
    @property
    def revision(self):
        return self.from_revision[0].revision

    @property
    def author(self):
        return self.from_revision[0].author

    @property
    def description(self):
        return self.from_revision[0].description


class VersionContent(DeletedVersionContent):
    """customized class for VersionContent entities"""
    id = 'VersionContent'
    __implements__ = DeletedVersionContent.__implements__ + (IDownloadable,)

    def dc_title(self):
        return self.req._('%(file)s (revision %(revision)s)') % {
            'file': self.file.path, 'revision': self.revision}

    def dc_long_title(self):
        rev = self.rev
        return self.req._('%(file)s (revision %(revision)s on %(date)s by %(author)s)') % {
            'file': self.file.path, 'revision': rev.revision,
            'author': rev.author, 'date': rev.printable_value('creation_date')}

    # IDownloadable
    def download_url(self):
        return self.absolute_url(vid='download')
    def download_content_type(self):
        return self.data_format
    def download_encoding(self):
        return self.data_encoding
    def download_file_name(self):
        return self.file.name
    def download_data(self):
        return self.data.getvalue()

    def size(self):
        rql = "Any LENGTH(D) WHERE X eid %(eid)s, X data D"
        return self.req.execute(rql, {'eid': self.eid})[0][0]

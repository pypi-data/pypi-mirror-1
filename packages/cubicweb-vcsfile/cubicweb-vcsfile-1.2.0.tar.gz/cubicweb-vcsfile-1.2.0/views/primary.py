"""primary views for entity types defined by the vcsfile package

:organization: Logilab
:copyright: 2007-2009 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
"""
__docformat__ = "restructuredtext en"
_ = unicode

from logilab.mtconverter import TransformError, xml_escape

from cubicweb.selectors import implements
from cubicweb.view import EntityView
from cubicweb.mttransforms import ENGINE
from cubicweb import tags
from cubicweb.web import uicfg
from cubicweb.web.views import (ibreadcrumbs, idownloadable,
                                baseviews, primary, tabs)

_pvs = uicfg.primaryview_section
_pvs.tag_attribute(('VersionedFile', 'name'), 'hidden')
_pvs.tag_attribute(('VersionedFile', 'directory'), 'hidden')
_pvs.tag_object_of(('*', 'from_repository', '*'), 'hidden')
for etype in ('DeletedVersionContent', 'VersionContent'):
    _pvs.tag_attribute((etype, 'revision'), 'hidden')
    _pvs.tag_attribute((etype, 'author'), 'hidden')
    _pvs.tag_subject_of((etype, 'content_for', '*'), 'hidden')


def render_entity_summary(self, entity):
    if entity.description:
        self.w(tags.div(entity.description, klass='summary'))
    if not entity.is_head(entity.rev.branch):
        msg = self._cw._('this file has newer revisions')
        self.w(tags.div(msg, klass='warning'))


class RepositoryPrimaryView(tabs.TabsMixin, primary.PrimaryView):
    __select__ = implements('Repository')

    tabs = [_('repositoryinfo_tab'), _('repositoryfiles_tab'), _('repositoryhistory_tab')]
    default_tab = 'repositoryinfo_tab'

    def cell_call(self, row, col):
        entity = self.cw_rset.get_entity(row, col)
        entity.complete()
        self.render_entity_title(entity)
        self.render_tabs(self.tabs, self.default_tab, entity)


class RepositoryInfoTab(primary.PrimaryView):
    __regid__ = 'repositoryinfo_tab'
    __select__ = implements('Repository')

    def render_entity_title(self, entity):
        pass

    def render_entity_attributes(self, entity):
        super(RepositoryInfoTab, self).render_entity_attributes(entity)
        rset = self._cw.execute('Any REV, REVB, REVN ORDERBY REVN DESC '
                                'WHERE REV branch REVB, REV revision REVN, REV from_repository R, '
                                'R eid %(r)s, NOT X parent_revision REV',
                                {'r': entity.eid}, 'r')
        if rset:
            self.w('<h3>%s</h3>' % self._cw._('heads'))
            self.wview('table', rset)


class RepositoryFilesTab(EntityView):
    __regid__ = 'repositoryfiles_tab'
    __select__ = implements('Repository')

    def cell_call(self, row, col):
        entity = self.rset.get_entity(row, col)
        filesrql = entity.related_rql('from_repository', 'object', ('VersionedFile',))
        self.wview('list', self._cw.execute(filesrql, {'x': entity.eid}, 'x'), 'noresult')


class RepositoryHistoryTab(EntityView):
    __regid__ = 'repositoryhistory_tab'
    __select__ = implements('Repository')

    def cell_call(self, row, col):
        entity = self.rset.get_entity(row, col)
        revisionsrql = entity.related_rql('from_repository', 'object', ('Revision',))
        self.wview('table', self._cw.execute(revisionsrql, {'x': entity.eid}, 'x'), 'noresult')


class DVCPrimaryView(primary.PrimaryView):
    __select__ = implements('DeletedVersionContent')

    def render_entity_title(self, entity):
        title = self._cw._('Revision %(revision)s of %(file)s: DELETED') % {
            'revision': entity.revision, 'file': entity.file.view('oneline')}
        self.w('<h1>%s</h1>' % title)

    render_entity_summary = render_entity_summary


class VCPrimaryView(idownloadable.IDownloadablePrimaryView):
    __select__ = implements('VersionContent')

    def render_entity_title(self, entity):
        title = self._cw._('Revision %(revision)s of %(file)s') % {
            'revision': entity.revision, 'file': entity.file.view('oneline')}
        self.w('<h1>%s</h1>' % title)

    render_entity_summary = render_entity_summary


class VCMetaDataView(baseviews.MetaDataView):
    """paragraph view of some metadata"""
    __select__ = implements('VersionContent', 'DeletedVersionContent')

    def cell_call(self, row, col):
        _ = self._cw._
        entity = self.cw_rset.get_entity(row, col)
        self.w(u'<div class="metadata">')
        self.w(u'#%s - ' % entity.eid)
        self.w(u'<span>%s</span> ' % _('revision %s of') % entity.revision)
        self.w(u'<span class="value">%s</span>,&nbsp;'
               % xml_escape(entity.file.path))
        self.w(u'<span>%s</span> ' % _('created on'))
        self.w(u'<span class="value">%s</span>'
               % entity.rev.printable_value('creation_date'))
        if entity.author:
            self.w(u'&nbsp;<span>%s</span> ' % _('by'))
            self.w(tags.span(entity.author, klass='value'))
        self.w(u'</div>')


class VFPrimaryView(primary.PrimaryView):
    __select__ = implements('VersionedFile')

    def render_entity_attributes(self, entity):
        super(VFPrimaryView, self).render_entity_attributes(entity)
        self.w(u'<div class="content">')
        if entity.deleted_in_branch():
            self.w(_('this file is currently deleted in the version control system'))
        else:
            head = entity.head
            contenttype = head.download_content_type()
            if contenttype.startswith('image/'):
                self.wview('image', head.rset, row=head.row)
            else:
                try:
                    if ENGINE.has_input(contenttype):
                        self.w(head.printable_value('data'))
                except TransformError:
                    pass
                except Exception, ex:
                    msg = self._cw._("can't display data, unexpected error: %s") % ex
                    self.w('<div class="error">%s</div>' % xml_escape(msg))
        self.w(u'</div>')

    def render_entity_relations(self, entity):
        revisions = entity.revisions
        self.w(u'<table class="listing">\n')
        self.w(u'<tr><th>%s</th><th>%s</th><th>%s</th><th>&nbsp;</th></tr>\n' %
               (_('revision'), _('author'), _('comment')))
        for vc in reversed(revisions):
            self.w(u'<tr><td><a href="%s">%s</a></td><td>%s</td><td>%s</td></tr>\n'
                   % (xml_escape(vc.absolute_url()), vc.revision,
                      xml_escape(vc.author or u''),
                      xml_escape(vc.description or u'')))
        self.w(u'</table>\n')


class RevisionPrimaryView(primary.PrimaryView):
    __select__ = implements('Revision')

    def render_entity_attributes(self, rev):
        self.field('description', xml_escape(rev.description))
        self.field('author', xml_escape(rev.author))
        if rev.branch:
            self.field('branch', xml_escape(rev.branch))
        self.field('from_repository', rev.repository.dc_title())
        parents = rev.related('parent_revision')
        if parents:
            self.field('parent_revision', self.view('csv', parents))
        children = rev.related('parent_revision', 'object')
        if children:
            self.field('parent_revision_object', self.view('csv', children))

    def render_entity_relations(self, rev):
        versioned = rev.reverse_from_revision
        if versioned:
            self.w(u'<table class="listing">')
            self.w(u'<tr><th>%s</th></tr>' %
                   self._cw._('objects concerned by this revision'))
            for obj in versioned:
                self.w(u'<tr><td><a href="%s">%s</a></td></tr>' % (
                    obj.absolute_url(), xml_escape(obj.dc_title())))
            self.w(u'</table>')
        else:
            self.w(u'<p>%s</p>' % self._cw._('this revision hasn\'t modified any files'))



class DVCBreadCrumbView(ibreadcrumbs.BreadCrumbView):
    __regid__ = 'breadcrumbtext'
    __select__ = implements('VersionContent', 'DeletedVersionContent')

    def cell_call(self, row, col):
        entity = self.rset.get_entity(row, col)
        self.w(entity.rev.dc_title())

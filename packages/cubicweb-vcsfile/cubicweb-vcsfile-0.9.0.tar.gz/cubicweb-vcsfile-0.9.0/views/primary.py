"""primary views for entity types defined by the vcsfile package

:organization: Logilab
:copyright: 2007-2009 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
"""
__docformat__ = "restructuredtext en"
_ = unicode

from logilab.mtconverter import TransformError, html_escape

from cubicweb.selectors import implements
from cubicweb.common import mttransforms, tags
from cubicweb.web import uicfg
from cubicweb.web.views.idownloadable import IDownloadablePrimaryView
from cubicweb.web.views.baseviews import MetaDataView
from cubicweb.web.views.primary import PrimaryView

def render_entity_metadata(self, entity):
    entity.view('metadata', w=self.w)
    if entity.description:
        self.w(tags.div(entity.description, klass='summary'))
    # XXX unless there is a standard way to pass the (mandatory) branch
    #     this breaks on hg repos
    #if not entity.is_head():
    #    msg = self.req._('this file has newer revisions')
    #    self.w(tags.div(msg, klass='warning'))

for etype in ('DeletedVersionContent', 'VersionContent'):
    uicfg.primaryview_section.tag_attribute((etype, 'revision'), 'hidden')
    uicfg.primaryview_section.tag_attribute((etype, 'author'), 'hidden')
    uicfg.primaryview_section.tag_subject_of((etype, 'content_for', '*'), 'hidden')

uicfg.primaryview_section.tag_attribute(('VersionedFile', 'name'), 'hidden')
uicfg.primaryview_section.tag_attribute(('VersionedFile', 'directory'), 'hidden')


class DVCPrimaryView(PrimaryView):
    __select__ = implements('DeletedVersionContent')

    def render_entity_title(self, entity):
        self.w(self.req._('Revision %(revision)s of %(file)s: DELETED')
               % {'revision': entity.revision,
                  'file': entity.file.view('oneline')})

    render_entity_metadata = render_entity_metadata


class VCPrimaryView(IDownloadablePrimaryView):
    __select__ = implements('VersionContent')

    def render_entity_title(self, entity):
        self.w(self.req._('Revision %(revision)s of %(file)s')
               % {'revision': entity.revision,
                  'file': entity.file.view('oneline')})

    render_entity_metadata = render_entity_metadata


class VCMetaDataView(MetaDataView):
    """paragraph view of some metadata"""
    __select__ = implements('VersionContent', 'DeletedVersionContent')

    def cell_call(self, row, col):
        _ = self.req._
        entity = self.entity(row, col)
        self.w(u'<div class="metadata">')
        self.w(u'#%s - ' % entity.eid)
        self.w(u'<span>%s</span> ' % _('revision %s of') % entity.revision)
        self.w(u'<span class="value">%s</span>,&nbsp;'
               % entity.file.path)
        self.w(u'<span>%s</span> ' % _('created on'))
        self.w(u'<span class="value">%s</span>'
               % self.format_date(entity.creation_date))
        if entity.author:
            self.w(u'&nbsp;<span>%s</span> ' % _('by'))
            self.w(tags.span(entity.author, klass='value'))
        self.w(u'</div>')


class VFPrimaryView(PrimaryView):
    __select__ = implements('VersionedFile')

    def render_entity_attributes(self, entity):
        super(VFPrimaryView, self).render_entity_attributes(entity)
        self.w(u'<div class="content">')
        if entity.revision_deleted():
            self.w(_('this file is currently deleted in the version control system'))
        else:
            head = entity.head
            contenttype = head.download_content_type()
            if contenttype.startswith('image/'):
                self.wview('image', head.rset, row=head.row)
            else:
                try:
                    if mttransforms.ENGINE.has_input(contenttype):
                        self.w(head.printable_value('data'))
                except TransformError:
                    pass
                except Exception, ex:
                    msg = self.req._("can't display data, unexpected error: %s") % ex
                    self.w('<div class="error">%s</div>' % msg)
        self.w(u'</div>')

    def render_entity_relations(self, entity):
        revisions = entity.revisions
        self.w(u'<table class="listing">\n')
        self.w(u'<tr><th>%s</th><th>%s</th><th>%s</th><th>&nbsp;</th></tr>\n' %
               (_('revision'), _('author'), _('comment')))
        for vc in reversed(revisions):
            self.w(u'<tr><td><a href="%s">%s</a></td><td>%s</td><td>%s</td></tr>\n'
                   % (html_escape(vc.absolute_url()), vc.revision,
                      html_escape(vc.author or u''),
                      html_escape(vc.description or u'')))
        self.w(u'</table>\n')


class RevisionPrimaryView(PrimaryView):
    __select__ = implements('Revision')

    def render_entity_attributes(self, rev):
        self.field('description', html_escape(rev.description))
        self.field('author', html_escape(rev.author))
        self.field('from_repository', rev.repository.dc_title())
        parents = rev.related('parent_revision')
        if parents:
            self.field('parent_revision', self.view('csv', parents))

    def render_entity_relations(self, rev):
        _ = self.req._
        self.w(u'<h2>%s</h2>' % _('Objects concerned by this revision'))
        versioned = rev.reverse_from_revision
        if versioned:
            self.w(u'<table class="listing">')
            self.w(u'<tr><th>%s</th></tr>' % _('objects concerned by this revision'))
            for obj in versioned:
                self.w(u'<tr><td><a href="%s">%s</a></td></tr>' % (
                    obj.absolute_url(), html_escape(obj.dc_title())))
            self.w(u'</table>')

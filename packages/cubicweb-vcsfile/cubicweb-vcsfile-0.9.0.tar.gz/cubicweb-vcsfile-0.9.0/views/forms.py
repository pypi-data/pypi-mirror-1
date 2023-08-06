"""custom forms to submit new revision to the svn repository or to edit
some information about existing revisions.

:organization: Logilab
:copyright: 2007-2009 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
"""
__docformat__ = "restructuredtext en"
_ = unicode

from copy import copy

from logilab.mtconverter import html_escape

from cubicweb.selectors import (match_form_params, match_kwargs,
                                implements, specified_etype_implements)
from cubicweb.view import EntityView
from cubicweb.common import tags
from cubicweb.web import (Redirect, controller, form,
                          formfields as fields, formwidgets as fwdgs)
from cubicweb.web.views import autoform, editforms


class RevisionCreationForm(autoform.AutomaticEntityForm):
    # vfeid needed for the inline-creation of VersionContent
    __select__ = specified_etype_implements('Revision') & match_form_params('vfeid')

    def should_display_inline_creation_form(self, rschema, existant, card):
        if rschema == 'from_revision':
            return True
        return super(RevisionCreationForm, self).should_display_inline_creation_form(
            rschema, existant, card)

    def default_author(self):
        return self.req.user.login


class VCInlinedCreationFormView(editforms.InlineEntityCreationFormView):
    # vfeid needed for the inline-creation of VersionContent
    __select__ = (match_form_params('vfeid') & match_kwargs('peid', 'rtype')
                  & specified_etype_implements('VersionContent'))

    def call(self, etype, peid, rtype, role='subject', **kwargs):
        """creation view for an entity"""
        vf = self.req.eid_rset(int(self.req.form['vfeid'])).get_entity(0, 0)
        self.orig_entity = vf.head
        # need a fully completed entity before doing the copy
        self.orig_entity.complete()
        if self.orig_entity.attr_metadata('data', 'format') in (
            'text/plain', 'text/html', 'text/rest'):
            # fill cache, Bytes fields are not loaded by complete()
            self.orig_entity.data
        entity = copy(self.orig_entity)
        self.initialize_varmaker()
        entity.eid = self.varmaker.next()
        self.render_form(entity, peid, rtype, role)

    def add_hiddens(self, form, entity, peid, rtype, role):
        super(VCInlinedCreationFormView, self).add_hiddens(
            form, entity, peid, rtype, role)
        form.form_add_hidden('content_for', self.orig_entity.file.eid,
                             eidparam=True)


class VCRevisionEditionForm(autoform.AutomaticEntityForm):
    # DeletedVersionContent has nothing editable
    __select__ = implements('VersionContent', 'Revision')
    attrcategories = ('primary', 'secondary', 'generated')
    EDITABLE_ATTRIBUTES = ('description', 'author', 'data_format', 'data_encoding')
    def editable_attributes(self):
        return [(rschema, x) for rschema, x in super(VCRevisionEditionForm, self).editable_attributes()
                if rschema.type in self.EDITABLE_ATTRIBUTES]


class VFUploadFormView(form.FormViewMixIn, EntityView):
    """form to upload a new revision of a versioned file"""
    id = 'vfnewrevform'
    __select__ = implements('VersionedFile')

    controller = 'vcsnewrev'

    def call(self, **_kwargs):
        # XXX explain why we would want self.rset.rowcount != 1
        for i in xrange(self.rset.rowcount):
            self.cell_call(i, 0)

    def form_title(self, entity):
        return self.req._('Upload a new revision of %s') % (
            '<a href="%s">%s</a>' % (html_escape(entity.absolute_url()),
                                     html_escape(entity.dc_title())))

    def cell_call(self, row, col, **kwargs):
        entity = self.entity(row, col)
        branches = entity.repository.branches()
        self.w(u'<div class="iformTitle">')
        self.w(self.form_title(entity))
        self.w(u'</div>')
        form = self.vreg.select_object('forms', 'base', self.req, entity=entity,
                                       action=self.build_url(self.controller),
                                       __redirectpath=entity.rest_path(),
                                       form_renderer_id='base',
                                       form_buttons=[fwdgs.SubmitButton()])
        form.append_field(fields.FileField(name=_('file'), eidparam=True))
        form.append_field(fields.StringField(name=_('branch'), required=True,
                                             eidparam=True, widget=fwdgs.Select,
                                             choices=branches))
        form.append_field(fields.StringField(label=_('commit message'),
                                             name='msg', eidparam=True))
        self.additional_form_fields(form, entity)
        # give default values so it won't try to get them from the entity
        self.w(form.form_render(file=u'', branch=u'', msg=u''))

    def additional_form_fields(self, form, entity):
        pass


class VFUploadController(controller.Controller):
    """upload a new revision of an already existing document"""
    id = 'vcsnewrev'

    def publish(self, rset=None):
        for eid in self.req.edited_eids():
            formparams = self.req.extract_entity_params(eid, minparams=2)
            vf = self.req.eid_rset(eid).get_entity(0, 0)
            vf.complete()
            self.upload_revision(vf, formparams)
        try:
            goto = self.req.build_url(self.req.form['__redirectpath'])
        except KeyError:
            goto = vf.absolute_url()
        raise Redirect(goto)

    def upload_revision(self, vf, formparams):
        # [-1] to discard file name and mime type
        stream = formparams['file'][-1]
        vf.vcs_upload_revision(stream, branch=formparams['branch'],
                               msg=formparams['msg'])
        return vf.eid


class VcsRmForm(form.FormViewMixIn, EntityView):
    id = 'vcsrmform'
    __select__ = implements('VersionedFile')

    def cell_call(self, row, col):
        entity = self.entity(row, col)
        self.w(u'<div class="iformTitle">')
        self.w(self.req._('DELETE the versioned file %(file)s') %
                    {'file': entity.view('incontext')})
        self.w(u'</div>')
        # XXX branch
        form = self.vreg.select_object('forms', 'base', self.req, self.rset,
                                       form_renderer_id='base', entity=entity,
                                       action=self.build_url('vcsrm'),
                                       form_buttons=[fwdgs.SubmitButton()])
        form.append_field(fields.RichTextField(name='msg', eidparam=True,
                                               label=_('commit message')))
        self.w(form.form_render(msg=''))


class VcsRmController(controller.Controller):
    """DELETE"""
    id = 'vcsrm'

    def publish(self, rset=None):
        req = self.req
        for eid in req.edited_eids():
            formparams = req.extract_entity_params(eid, minparams=2)
            vf = self.req.eid_rset(eid).get_entity(0, 0)
            vf.vcs_rm(msg=formparams['msg'])
        msg = req._('file was marked DELETED')
        raise Redirect(vf.absolute_url(__message=msg))

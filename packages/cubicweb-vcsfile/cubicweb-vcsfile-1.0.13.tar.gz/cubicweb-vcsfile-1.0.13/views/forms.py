"""custom forms to submit new revision to the svn repository or to edit
some information about existing revisions.

:organization: Logilab
:copyright: 2007-2010 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
"""
__docformat__ = "restructuredtext en"
_ = unicode

from copy import copy

from logilab.mtconverter import xml_escape
from logilab.common.decorators import cached

from cubicweb.selectors import (match_form_params, match_kwargs,
                                implements, entity_implements,
                                specified_etype_implements)
from cubicweb.view import EntityView
from cubicweb.common import tags
from cubicweb.web import (Redirect, controller, form,
                          formfields as fields, formwidgets as fwdgs)
from cubicweb.web.views import autoform, editforms, forms

from cubes.vcsfile import IMMUTABLE_ATTRIBUTES


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

    if hasattr(editforms.InlineEntityCreationFormView, 'form'):

        # cw > 3.5.2
        @cached
        def _entity(self):
            """creation view for an entity"""
            vf = self.req.entity_from_eid(int(self.req.form['vfeid']))
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
            return entity

        def add_hiddens(self, form, entity):
            super(VCInlinedCreationFormView, self).add_hiddens(
                form, entity)
            form.form_add_hidden('content_for', self.orig_entity.file.eid,
                                 eidparam=True)

    else:

        def call(self, etype, peid, rtype, role='subject', **kwargs):
            """creation view for an entity"""
            vf = self.req.entity_from_eid(int(self.req.form['vfeid']))
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

def filter_out_immutable_rels(func):
    def wrapper(self, *args, **kwargs):
        entity = self.edited_entity
        if entity.has_eid():
            immutable = IMMUTABLE_ATTRIBUTES
        else:
            immutable = ('Revision.revision',)
        for rschema, tschemas, role in func(self, *args, **kwargs):
            if role == 'subject':
                etype = entity.id
            # take care, according to the wrapped function tschemas is a list or
            # a single schema
            elif isinstance(tschemas, list):
                etype = tschemas[0]
            else:
                etype = tschemas
            if '%s.%s' % (etype, rschema) in immutable:
                continue
            yield rschema, tschemas, role
    return wrapper


class VCRevisionEditionForm(autoform.AutomaticEntityForm):
    __select__ = implements('Revision', 'VersionedFile',
                            'VersionContent', 'DeletedVersionContent')
    if hasattr(autoform.AutomaticEntityForm, '_relations_by_section'):
        # cw 3.6
        _relations_by_section = filter_out_immutable_rels(
            autoform.AutomaticEntityForm._relations_by_section)
    else:
        relations_by_category = filter_out_immutable_rels(
            autoform.AutomaticEntityForm.relations_by_category)
        srelations_by_category = filter_out_immutable_rels(
            autoform.AutomaticEntityForm.srelations_by_category)
        inlined_relations = filter_out_immutable_rels(
            autoform.AutomaticEntityForm.inlined_relations)


def available_branches(form):
    return form.edited_entity.repository.branches()


class NewRevisionForm(forms.EntityFieldsForm):
    id = 'vfnewrevform'
    __select__ = entity_implements('VersionedFile')

    form_renderer_id = 'base'
    form_buttons = [fwdgs.SubmitButton()]

    file = fields.FileField(eidparam=True)
    branch = fields.StringField(required=True, eidparam=True,
                                widget=fwdgs.Select, choices=available_branches,
                                # XXX in 3.6, uncomment this / remove formvalues
                                #initial=lambda formentity.repository.default_branch()
                                )
    msg = fields.StringField(label=_('commit message'), eidparam=True)


class VFUploadFormView(form.FormViewMixIn, EntityView):
    """form to upload a new revision of a versioned file"""
    id = 'vfnewrevform'
    __select__ = implements('VersionedFile')

    submitmsg = _('new revision has been checked-in')
    action = 'vcsnewrev'

    def call(self, **_kwargs):
        # XXX explain why we would want self.rset.rowcount != 1
        for i in xrange(self.rset.rowcount):
            self.cell_call(i, 0)

    def form_title(self, entity):
        return self.req._('Upload a new revision of %s') % (
            '<a href="%s">%s</a>' % (xml_escape(entity.absolute_url()),
                                     xml_escape(entity.dc_title())))

    def cell_call(self, row, col, **kwargs):
        entity = self.entity(row, col)
        self.w(u'<div class="iformTitle">')
        self.w(self.form_title(entity))
        self.w(u'</div>')
        form = self.vreg['forms'].select(
            'vfnewrevform', self.req, entity=entity,
            submitmsg=self.req._(self.submitmsg), action=self.action,
            __redirectpath=entity.rest_path(),)
        self.additional_form_fields(form, entity)
        # give default values so it won't try to get them from the entity
        self.w(form.render(formvalues=dict(branch=entity.repository.default_branch(),
                                           file=u'', msg=u'')))

    def additional_form_fields(self, form, entity):
        pass


class VFUploadController(controller.Controller):
    """upload a new revision of an already existing document"""
    id = 'vcsnewrev'

    def publish(self, rset=None):
        for eid in self.req.edited_eids():
            formparams = self.req.extract_entity_params(eid, minparams=2)
            vf = self.req.entity_from_eid(eid)
            vf.complete()
            self.upload_revision(vf, formparams)
        try:
            kwargs = {'__message': self.req.form['__message']}
        except KeyError:
            kwargs = {}
        try:
            goto = self.req.build_url(self.req.form['__redirectpath'], **kwargs)
        except KeyError:
            goto = vf.absolute_url(**kwargs)
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
        form.append_field(fields.StringField(name='msg', eidparam=True,
                                             label=_('commit message')))
        self.w(form.form_render(msg=''))


class VcsRmController(controller.Controller):
    """DELETE"""
    id = 'vcsrm'

    def publish(self, rset=None):
        req = self.req
        for eid in req.edited_eids():
            formparams = req.extract_entity_params(eid, minparams=2)
            vf = self.req.entity_from_eid(eid)
            vf.vcs_rm(msg=formparams['msg'])
        msg = req._('file was marked DELETED')
        raise Redirect(vf.absolute_url(__message=msg))

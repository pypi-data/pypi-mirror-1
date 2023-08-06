"""app objects for vcsfile web interface"""

from cubicweb.web import uicfg
from cubicweb.web.formfields import EditableFileField
from cubicweb.web import formwidgets as wdgs

# hidden fields in edition
_afs = uicfg.autoform_section
_afs.tag_attribute(('Revision', 'revision'), 'generated')
_afs.tag_attribute(('Revision', 'changeset'), 'generated')
_afs.tag_subject_of(('*', 'content_for', 'VersionedFile'), 'generated')
_afs.tag_object_of(('*', 'content_for', 'VersionedFile'), 'generated')

# widgets / fields adjustement
_aff = uicfg.autoform_field
_affk = uicfg.autoform_field_kwargs
_aff.tag_attribute(('VersionContent', 'data'), EditableFileField)
_affk.tag_attribute(('VersionContent', 'data'), {'required': True})
_affk.tag_attribute(('Repository', 'path'), {'widget': wdgs.TextInput})
_affk.tag_attribute(('Repository', 'subpath'), {'widget': wdgs.TextInput})
_affk.tag_attribute(('VersionedFile', 'directory'), {'widget': wdgs.TextInput})
_affk.tag_attribute(('VersionedFile', 'name'), {'widget': wdgs.TextInput})

# inlined relation in edition
_afii = uicfg.autoform_is_inlined
_afii.tag_object_of(('VersionContent', 'from_revision', '*'), True)

# primary view tweaks
_pvs = uicfg.primaryview_section
_pvdc = uicfg.primaryview_display_ctrl
# internal purpose relation
_pvs.tag_subject_of(('*', 'at_revision', '*'), 'hidden')
_pvs.tag_object_of(('*', 'at_revision', '*'), 'hidden')
# displayed in attributes/relations section of Revision primary view
_pvs.tag_subject_of(('*', 'parent_revision', '*'), 'hidden')
_pvs.tag_object_of(('*', 'parent_revision', '*'), 'hidden')
_pvs.tag_object_of(('*', 'from_revision', '*'), 'hidden')
_pvdc.tag_subject_of(('*', 'from_revision', '*'), {'vid': 'incontext'})
_pvdc.tag_subject_of(('*', 'from_repository', '*'), {'vid': 'incontext'})
_pvdc.tag_subject_of(('*', 'content_for', '*'), {'vid': 'incontext'})

# we don't want automatic addrelated action for the following relations...
_abaa = uicfg.actionbox_appearsin_addmenu
for rtype in ('from_repository', 'from_revision', 'content_for',
              'parent_revision'):
    _abaa.tag_object_of(('*', rtype, '*'), False)

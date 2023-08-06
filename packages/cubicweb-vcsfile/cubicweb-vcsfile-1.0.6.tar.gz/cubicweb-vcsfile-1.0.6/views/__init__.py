"""app objects for vcsfile web interface"""

from cubicweb.web import uicfg
from cubicweb.web.formfields import EditableFileField
from cubicweb.web import formwidgets as wdgs

# hidden fields in edition
_afs = uicfg.autoform_section
_afs.tag_attribute(('Repository', 'latest_known_revision'), 'generated')
_afs.tag_attribute(('Revision', 'revision'), 'generated')
_afs.tag_attribute(('Revision', 'changeset'), 'generated')

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

# ensure we don't propose to add DeletedVersionContent for a VersionedFile
# this has to be handled manually to avoid proposing to "add" something that
# will "remove" something...
_abaa = uicfg.actionbox_appearsin_addmenu
_abaa.tag_object_of(('DeletedVersionContent', 'content_for', 'VersionedFile'),
                    False)

"""app objects for vcsfile web interface"""

from cubicweb.web import uicfg
from cubicweb.web.formfields import EditableFileField
from cubicweb.web import formwidgets

# widgets / fields adjustement
uicfg.autoform_field.tag_attribute(('VersionContent', 'data'), EditableFileField)

uicfg.autoform_field_kwargs.tag_attribute(('Repository', 'path'),
                                          {'widget': formwidgets.TextInput})
uicfg.autoform_field_kwargs.tag_attribute(('Repository', 'subpath'),
                                          {'widget': formwidgets.TextInput})
uicfg.autoform_field_kwargs.tag_attribute(('VersionedFile', 'directory'),
                                          {'widget': formwidgets.TextInput})
uicfg.autoform_field_kwargs.tag_attribute(('VersionedFile', 'name'),
                                          {'widget': formwidgets.TextInput})

# hidden fields in edition
uicfg.autoform_section.tag_attribute(('Repository', 'latest_known_revision'), 'generated')
uicfg.autoform_section.tag_attribute(('Revision', 'revision'), 'generated')
uicfg.autoform_section.tag_attribute(('Revision', 'changeset'), 'generated')

# inlined relation in edition
uicfg.autoform_is_inlined.tag_object_of(('VersionContent', 'from_revision', '*'), True)


uicfg.actionbox_appearsin_addmenu.tag_object_of(
    ('DeletedVersionContent', 'content_for', 'VersionedFile'), False)

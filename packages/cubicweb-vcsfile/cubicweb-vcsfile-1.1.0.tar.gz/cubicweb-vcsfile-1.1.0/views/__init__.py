"""app objects for vcsfile web interface"""

from cubicweb.web import uicfg

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

from cubes.vcsfile.vcssource import get_vcs_source

session.set_pool()
cu = session.pool[get_vcs_source(session.repo).uri]

try:
    cu.execute('CREATE TABLE at_revision_relation (eid_from integer, eid_to integer)')
    cu.execute('ALTER TABLE cw_VersionContent ADD COLUMN cw_vc_copy integer')
    cu.execute('ALTER TABLE cw_VersionContent ADD COLUMN cw_vc_rename integer')
except:
    print 'tables already altered'
else:
    add_relation_type('at_revision')
    add_relation_type('vc_copy')
    add_relation_type('vc_rename')


session.set_pool()
from cubes.vcsfile.vcssource import set_at_revision

rset = rql('Revision X ORDERBY X', ask_confirm=False)
for reid, in rset:
    print 'set at rev', reid
    set_at_revision(session, reid)
checkpoint()

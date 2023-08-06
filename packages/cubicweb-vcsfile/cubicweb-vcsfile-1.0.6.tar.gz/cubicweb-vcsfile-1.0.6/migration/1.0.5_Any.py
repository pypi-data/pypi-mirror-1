from time import time

add_relation_type('ancestor_revision')

rset = rql('Revision X ORDERBY R WHERE X revision R', ask_confirm=False)
for reid, in rset:
    print 'set ancestor for', reid,
    t = time()
    rql('SET REV ancestor_revision PREV WHERE REV eid %(rev)s, REV parent_revision PREV',
        {'rev': reid}, 'rev', ask_confirm=False)
    rql('SET REV ancestor_revision AREV WHERE REV eid %(rev)s, REV parent_revision PREV, '
        'PREV ancestor_revision AREV', {'rev': reid}, 'rev', ask_confirm=False)
    print '%.3f sec.' % (time() - t)

checkpoint()

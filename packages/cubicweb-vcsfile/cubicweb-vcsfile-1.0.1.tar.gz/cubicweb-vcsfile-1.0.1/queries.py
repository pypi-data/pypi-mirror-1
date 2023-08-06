
def new_revision_rql(has_parent, set_all=False):
    """return rql to insert a revision entity

    substitutions used:
    * description, author, branch, repoeid (mandatory)
    * parent (if `has_parent` is True)
    * date, revision, changeset (if `set_all` is True)
    """
    rql = ('INSERT Revision R: R description %(description)s, '
           'R author %(author)s, R branch %(branch)s, R from_repository X')
    if set_all:
        rql += ', R revision %(revision)s, R changeset %(changeset)s'
        rql += ', R creation_date %(date)s, R modification_date %(date)s'
    if has_parent:
        rql += ', R parent_revision PR'
    rql += ' WHERE X eid %(repoeid)s'
    if has_parent:
        rql += ', PR eid %(parent)s'
    return rql

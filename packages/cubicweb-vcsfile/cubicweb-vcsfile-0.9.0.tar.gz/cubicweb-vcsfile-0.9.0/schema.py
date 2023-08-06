"""entity types used to represent a version control system (vcs) content

:organization: Logilab
:copyright: 2007-2009 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
"""
__docformat__ = "restructuredtext en"


class Repository(EntityType):
    """a local subversion repository which will be used as versionned content
    entity source
    """
    permissions = {
        'read':   ('managers', 'users'),
        'add':    ('managers',),
        'update': ('managers',),
        'delete': ('managers',),
        }
    type = String(required=True, vocabulary=('subversion', 'mercurial'),
                  description=_('repository\'s type'))
    path = String(required=True, unique=True,
                  description=_('path to the repository'))
    subpath = String(description=_('if specified, only import the given subpart'
                                   ' of the repository (path relative to the '
                                   'repository root)'))
    encoding = String(default='utf-8', maxsize=20, required=True,
                      description=_('encoding used for the repository (e.g.'
                                    ' for file path and check-in comments)'))
    latest_known_revision = Int(default=0,
                                description=_('latest revision known by the '
                                              'source for this repository'))


class Revision(EntityType):
    permissions = {
        'read':   ('managers', 'users', 'guests'),
        'add':    ('managers', 'users',),
        'update': ('managers', 'owners'),
        'delete': (),
        }
    # NOTE: creation_date will be set at revision date
    revision = Int(required=True, indexed=True,
                   description=_('revision number.'))

    description = String(fulltextindexed=True, description=_('comment for this revision.'))

    author = String(indexed=True, fulltextindexed=True, maxsize=200,
                    description=_("author of this revision."))

    changeset = String(indexed=True, maxsize=100,
                       description=_('change set identifier, when used by the '
                                     'underlying version control system.'))

    branch = String(indexed=True, maxsize=255,
                    description=_("branch of this revision."))
    # XXX tags

    from_repository = SubjectRelation('Repository', cardinality='1*', composite='object')
    parent_revision = SubjectRelation('Revision')


class VersionedFile(EntityType):
    """a file stored in a versioned source"""
    permissions = {
        'read':   ('managers', 'users', 'guests'),
        'add':    ('managers', 'users',),
        'update': (),
        'delete': (),
        }
    directory = String(required=True, fulltextindexed=True, indexed=True,
                       description=_('directory of the file in the repository.'))
    name = String(required=True, fulltextindexed=True,
                  description=_('name of the file in the repository.'))
    from_repository = SubjectRelation('Repository', cardinality='1*', composite='object')


class DeletedVersionContent(EntityType):
    """represent a revision where a versioned file has been deleted"""
    permissions = {
        'read':   ('managers', 'users', 'guests'),
        'add':    ('managers', 'users',),
        'update': ('managers', 'owners'),
        'delete': (),
        }
    from_revision = SubjectRelation('Revision', cardinality='1*', composite='object')
    at_revision = SubjectRelation('Revision')


class VersionContent(DeletedVersionContent):
    """actual content of a versioned file, for a given revision"""

    data = Bytes(required=True, fulltextindexed=True,
                 description=_("file's data"))
    data_format = String(required=True, meta=True, maxsize=50,
                         description=_('MIME type of the file.'))
    data_encoding = String(meta=True, maxsize=20,
                           description=_('encoding of the file when it applies (e.g. text).'))

    vc_copy = SubjectRelation('VersionContent', cardinality='?*')
    vc_rename = SubjectRelation('VersionContent', cardinality='?*')


class from_repository(RelationType):
    # NOTE: should't be inlined since Repository entities are stored outside the
    # vcs source
    pass

class content_for(RelationType):
    subject = ('DeletedVersionContent', 'VersionContent')
    object = 'VersionedFile'
    composite = 'object'
    cardinality = '1*'
    inlined = True # how ?

class from_revision(RelationType):
    inlined = True

class at_revision(RelationType):
    permissions = {
        'read':   ('managers', 'users', 'guests'),
        'add':    (),
        'delete': (),
        }

class vc_copy(RelationType):
    inlined = True

class vc_rename(RelationType):
    inlined = True

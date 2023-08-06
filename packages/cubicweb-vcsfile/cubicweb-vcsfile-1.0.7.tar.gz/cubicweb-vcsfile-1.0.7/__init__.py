"""cubicweb-vcsfile"""

try:
    from cubicweb import server
except ImportError:
    # no server part
    pass
else:
    from logilab.common.modutils import LazyObject
    server.SOURCE_TYPES['vcsfile'] = LazyObject('cubes.vcsfile.vcssource',
                                                'VCSSource')

from cubicweb import ETYPE_NAME_MAP
ETYPE_NAME_MAP['Versionedfile'] = 'VersionedFile'
ETYPE_NAME_MAP['Deletedversioncontent'] = 'DeletedVersionContent'
ETYPE_NAME_MAP['Versioncontent'] = 'VersionContent'


IMMUTABLE_ATTRIBUTES = frozenset(('VersionedFile.directory',
                                  'VersionedFile.name',
                                  'VersionedFile.from_repository',
                                  'Revision.revision',
                                  'Revision.changeset',
                                  'Revision.branch',
                                  'Revision.from_repository',
                                  'DeletedVersionContent.from_revision',
                                  'DeletedVersionContent.content_for',
                                  'VersionContent.from_revision',
                                  'VersionContent.content_for',
                                  'VersionContent.data',
                                  ))

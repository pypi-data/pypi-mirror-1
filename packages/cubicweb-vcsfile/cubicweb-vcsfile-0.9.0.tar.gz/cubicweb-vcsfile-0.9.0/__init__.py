"""vcsfile cubicweb package : interface local svn repository content as cubicweb
entities

:organization: Logilab
:copyright: 2007-2009 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
"""

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

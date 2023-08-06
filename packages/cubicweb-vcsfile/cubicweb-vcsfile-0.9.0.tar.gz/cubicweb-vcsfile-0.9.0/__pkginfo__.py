# pylint: disable-msg=W0622
"""cubicweb-vcsfile packaging information"""

distname = "cubicweb-vcsfile"
modname = distname.split('-', 1)[1]

numversion = (0, 9, 0)
version = '.'.join(str(num) for num in numversion)

copyright = '''Copyright (c) 2007-2009 LOGILAB S.A. (Paris, FRANCE).
http://www.logilab.fr/ -- mailto:contact@logilab.fr'''

license = 'LGPL'
author = "Logilab"
author_email = "contact@logilab.fr"
web = 'http://www.cubicweb.org/project/%s' % modname

short_desc = "Interface local versioned files repository content as cubicweb entities"
long_desc = """Cubicweb is a entities / relations bases knowledge management system
developped at Logilab.
.
This package provides a custom source as well as custom entity types and
views to provide transparent access of files versioned in subversion or
mercurial repositories.
.
"""

from os import listdir
from os.path import join

CUBES_DIR = join('share', 'cubicweb', 'cubes')
try:
    data_files = [
        [join(CUBES_DIR, 'vcsfile'),
         [fname for fname in listdir('.')
          if fname.endswith('.py') and fname != 'setup.py']],
        [join(CUBES_DIR, 'vcsfile', 'views'),
         [join('views', fname) for fname in listdir('views')
          if not fname.endswith('.pyc')]],
        #[join(CUBES_DIR, 'vcsfile', 'data'),
        # [join('data', fname) for fname in listdir('data')]],
        [join(CUBES_DIR, 'vcsfile', 'i18n'),
         [join('i18n', fname) for fname in listdir('i18n')]],
        [join(CUBES_DIR, 'vcsfile', 'migration'),
         [join('migration', fname) for fname in listdir('migration')]],
        ]
except OSError:
    # we are in an installed directory
    pass

cube_eid = None # XXX
# used packages
__use__ = ()

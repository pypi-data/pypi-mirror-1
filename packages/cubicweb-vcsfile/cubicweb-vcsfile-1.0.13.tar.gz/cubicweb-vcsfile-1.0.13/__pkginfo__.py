# pylint: disable-msg=W0622
"""cubicweb-vcsfile packaging information"""

modname = 'vcsfile'
distname = "cubicweb-%s" % modname

numversion = (1, 0, 13)
version = '.'.join(str(num) for num in numversion)

copyright = '''Copyright (c) 2007-2010 LOGILAB S.A. (Paris, FRANCE).
http://www.logilab.fr/ -- mailto:contact@logilab.fr'''

license = 'LGPL'
author = "Logilab"
author_email = "contact@logilab.fr"
web = 'http://www.cubicweb.org/project/%s' % distname

short_desc = "component to use version control systems from the CubicWeb framework"
long_desc = """CubicWeb VCSFile component to integrate with version control systems and
make their data available from within a CubicWeb application (currently
works for mercurial and subversion).

CubicWeb is a semantic web application framework, see http://www.cubicweb.org
"""

from os import listdir as _listdir
from os.path import join, isdir
from glob import glob

THIS_CUBE_DIR = join('share', 'cubicweb', 'cubes', modname)

def listdir(dirpath):
    return [join(dirpath, fname) for fname in _listdir(dirpath)
            if fname[0] != '.' and not fname.endswith('.pyc')
            and not fname.endswith('~')
            and not isdir(join(dirpath, fname))]

data_files = [
    # common files
    [THIS_CUBE_DIR, [fname for fname in glob('*.py') if fname != 'setup.py']],
    ]
# check for possible extended cube layout
for dirname in ('entities', 'views', 'sobjects', 'hooks', 'schema', 'data', 'i18n', 'migration'):
    if isdir(dirname):
        data_files.append([join(THIS_CUBE_DIR, dirname), listdir(dirname)])
# Note: here, you'll need to add subdirectories if you want
# them to be included in the debian package

cube_eid = None # XXX
# used packages
__depends_cubes__ = {}
__depends__ = {'cubicweb': '>= 3.3.1',
               'logilab-mtconverter': '>= 0.7.0',
               'pysqlite': None,
               }
__use__ = tuple(__depends_cubes__)
classifiers = [
           'Environment :: Web Environment',
           'Framework :: CubicWeb',
           'Programming Language :: Python',
           'Programming Language :: JavaScript',
           ]

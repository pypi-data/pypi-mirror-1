# pylint: disable-msg=W0622
"""cubicweb-apycot application packaging information"""

modname = 'apycot'
distname = 'cubicweb-apycot'

numversion = (1, 7, 0)
version = '.'.join(str(num) for num in numversion)

license = 'GPL'
copyright = '''Copyright (c) 2008-2010 LOGILAB S.A. (Paris, FRANCE).
http://www.logilab.fr/ -- mailto:contact@logilab.fr'''

author = 'Logilab'
author_email = 'contact@logilab.fr'

short_desc = 'apycot component for the CubicWeb framework'
long_desc = '''This CubicWeb component store data from the Apycot testing framework
and provides multi-criteria reports.

CubicWeb is a semantic web application framework, see http://www.cubicweb.org
'''

web = 'http://www.cubicweb.org/project/%s' % distname

classifiers = [
    'Environment :: Web Environment',
    'Framework :: CubicWeb',
    'Programming Language :: Python',
    'Programming Language :: JavaScript',
    ]

pyversions = ['2.4']

__depends_cubes__ = {'vcsfile': '>= 0.9.0'}
__depends__ = {'cubicweb': '>= 3.6.0', 'pyro': None}
for key,value in __depends_cubes__.items():
    __depends__['cubicweb-'+key] = value
__use__ = tuple(__depends_cubes__)
__recommends__ = {'tracker': None, 'nosylist': None}
__recommend__ = tuple(__recommends__)

from os import listdir as _listdir
from os.path import join, isdir

#from cubicweb.devtools.pkginfo import get_distutils_datafiles
CUBES_DIR = join('share', 'cubicweb', 'cubes')
THIS_CUBE_DIR = join(CUBES_DIR, 'apycot')

def listdir(dirpath):
    return [join(dirpath, fname) for fname in _listdir(dirpath)
            if fname[0] != '.' and not fname.endswith('.pyc')
            and not fname.endswith('~')]

from glob import glob
try:
    data_files = [
        # common files
        [THIS_CUBE_DIR, [fname for fname in glob('*.py') if fname != 'setup.py']],
        ]

    # check for possible extended cube layout
    for dirname in ('entities', 'views', 'sobjects', 'schema', 'data', 'i18n', 'migration'):
        if isdir(dirname):
            data_files.append([join(THIS_CUBE_DIR, dirname), listdir(dirname)])
    # Note: here, you'll need to add subdirectories if you want
    # them to be included in the debian package
except OSError:
    # we are in an installed directory
    pass

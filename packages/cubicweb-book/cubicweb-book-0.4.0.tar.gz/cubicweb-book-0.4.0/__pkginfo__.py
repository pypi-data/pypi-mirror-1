# pylint: disable-msg=W0622
"""cubicweb-book application packaging information"""

modname = 'book'
distname = 'cubicweb-%s' % modname

numversion = (0, 4, 0)
version = '.'.join(str(num) for num in numversion)

license = 'LGPL'
copyright = '''Copyright (c) 2008-2010 LOGILAB S.A. (Paris, FRANCE).
http://www.logilab.fr/ -- mailto:contact@logilab.fr'''

author = 'Logilab'
author_email = 'contact@logilab.fr'

short_desc = 'book component for the CubicWeb framework'
long_desc = '''This CubicWeb component is used to model books.

CubicWeb is a semantic web framework, see http://www.cubicweb.org
'''

from os import listdir as _listdir
from os.path import join, isdir, dirname as _dirname

from glob import glob
scripts = glob(join('bin', 'book-*'))

ftp = ''
web = 'http://www.cubicweb.org/project/%s' % distname

pyversions = ['2.4']

classifiers = [
    'Environment :: Web Environment',
    'Framework :: CubicWeb',
    'Programming Language :: Python',
    'Programming Language :: JavaScript',
    ]

__depends_cubes__ = {'addressbook': None,
                     'person': None,
                     'file': None
                     }
__depends__ = {'cubicweb': '>= 3.6.0'}
for key, value in __depends_cubes__.items():
    __depends__['cubicweb-'+key] = value
__use__ = tuple(__depends_cubes__)

#from cubicweb.devtools.pkginfo import get_distutils_datafiles
CUBES_DIR = join('share', 'cubicweb', 'cubes')
THIS_CUBE_DIR = join(CUBES_DIR, 'book')

def listdir(dirpath):
    abspath = join(_dirname(__file__), dirpath)
    return [join(dirpath, fname) for fname in _listdir(abspath)
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
data_files.append([join(THIS_CUBE_DIR, 'data/images'),  listdir('data/images')],)

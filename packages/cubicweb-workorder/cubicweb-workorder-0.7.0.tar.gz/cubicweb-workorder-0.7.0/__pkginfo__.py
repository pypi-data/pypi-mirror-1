# pylint: disable-msg=W0622
"""cubicweb-workorder application packaging information"""

modname = 'workorder'
distname = 'cubicweb-%s' % modname

numversion = (0, 7, 0)
version = '.'.join(str(num) for num in numversion)

license = 'LGPL'
copyright = '''Copyright (c) 2008-2010 LOGILAB S.A. (Paris, FRANCE).
http://www.logilab.fr/ -- mailto:contact@logilab.fr'''

author = 'Logilab'
author_email = 'contact@logilab.fr'

short_desc = 'workorder component for the CubicWeb framework'
long_desc = '''CubicWeb WorkOrder component for modeling orders and workorders
(an order can be split into several workorders).

CubicWeb is a semantic web framework, see http://www.cubicweb.org
'''

from os import listdir as _listdir
from os.path import join, isdir

from glob import glob
scripts = glob(join('bin', 'workorder-*'))

web = 'http://www.cubicweb.org/project/%s' % distname

pyversions = ['2.4']

#from cubicweb.devtools.pkginfo import get_distutils_datafiles
CUBES_DIR = join('share', 'cubicweb', 'cubes')
THIS_CUBE_DIR = join(CUBES_DIR, 'workorder')

def listdir(dirpath):
    return [join(dirpath, fname) for fname in _listdir(dirpath)
            if fname[0] != '.' and not fname.endswith('.pyc')
            and not fname.endswith('~')]

try:
    data_files = [
        # common files
        [THIS_CUBE_DIR, [fname for fname in glob('*.py') if fname != 'setup.py']],

        # client (web) files
        [join(THIS_CUBE_DIR, 'data'),  listdir('data')],
        [join(THIS_CUBE_DIR, 'i18n'),  listdir('i18n')],

        # server files
        [join(THIS_CUBE_DIR, 'migration'), listdir('migration')],
        ]

    # check for possible extended template layout
    for dirname in ('entities', 'views', 'sobjects', 'schema'):
        if isdir(dirname):
            data_files.append([join(THIS_CUBE_DIR, dirname), listdir(dirname)])
    # Note: here, you'll need to add subdirectories if you want
    # them to be included in the debian package
except OSError:
    # we are in an installed directory
    pass


__depends_cubes__ = {}
__depends__ = {'cubicweb': '>= 3.6.0'}
__use__ = tuple(__depends_cubes__)
classifiers = [
           'Environment :: Web Environment',
           'Framework :: CubicWeb',
           'Programming Language :: Python',
           'Programming Language :: JavaScript',
]

# pylint: disable-msg=W0622
"""cubicweb-skillmat application packaging information"""

modname = 'skillmat'
distname = 'cubicweb-skillmat'

numversion = (0, 7, 0)
version = '.'.join(str(num) for num in numversion)

license = 'LGPL'
copyright = '''Copyright (c) 2008-2010 LOGILAB S.A. (Paris, FRANCE).
http://www.logilab.fr/ -- mailto:contact@logilab.fr'''

author = 'Logilab'
author_email = 'contact@logilab.fr'

web = 'http://www.cubicweb.org/project/%s' % distname

short_desc = 'skill matrix component for the CubicWeb framework'
long_desc = '''This CubicWeb component models the skills of a team
(who can do what at which level of expertise).

CubicWeb is a semantic web application framework, see http://www.cubicweb.org
'''

classifiers = [
    'Environment :: Web Environment',
    'Framework :: CubicWeb',
    'Programming Language :: Python',
    'Programming Language :: JavaScript',
    ]

__depends_cubes__ = {'folder': None,
                     'comment': None}
__depends__ = {'cubicweb': '>= 3.6.0'}
for key, value in __depends_cubes__.items():
    __depends__['cubicweb-'+key] = value
__use__ = tuple(__depends_cubes__)

# packaging

from glob import glob
from os import listdir as _listdir
from os.path import join, isdir

pyversions = ['2.4']

#from cubicweb.devtools.pkginfo import get_distutils_datafiles
CUBES_DIR = join('share', 'cubicweb', 'cubes')
THIS_CUBE_DIR = join(CUBES_DIR, 'skillmat')

def listdir(dirpath):
    return [join(dirpath, fname) for fname in _listdir(dirpath)
            if fname[0] != '.' and not fname.endswith('.pyc')
            and not fname.endswith('~')]

try:
    data_files = [
        # common files
        [THIS_CUBE_DIR, [fname for fname in glob('*.py') if fname != 'setup.py']],

        [join(THIS_CUBE_DIR, 'entities'), listdir('entities')],

        # client (web) files
        [join(THIS_CUBE_DIR, 'data'),  listdir('data')],
        [join(THIS_CUBE_DIR, 'i18n'),  listdir('i18n')],
        [join(THIS_CUBE_DIR, 'views'), listdir('views')],
        [join(THIS_CUBE_DIR, 'wdoc'), listdir('wdoc')],
        # Note: here, you'll need to add views' subdirectories if you want
        # them to be included in the debian package

        # server files
        [join(THIS_CUBE_DIR, 'migration'), listdir('migration')],
        ]
except OSError, xx:
    # we are in an installed directory
    pass

cube_eid = None # <=== FIXME if you need direct bug-subscription

# pylint: disable-msg=W0622
"""cubicweb-company application packaging information"""

modname = 'company'
distname = 'cubicweb-%s' % modname

numversion = (0, 5, 0)
version = '.'.join(str(num) for num in numversion)

license = 'LGPL'
copyright = '''Copyright (c) 2008-2010 LOGILAB S.A. (Paris, FRANCE).
http://www.logilab.fr/ -- mailto:contact@logilab.fr'''

author = 'Logilab'
author_email = 'contact@logilab.fr'

short_desc = 'company component for the CubicWeb framework'
long_desc = '''This CubicWeb component models companies and divisions (divisions are
parts of companies).

CubicWeb is a semantic web application framework, see http://www.cubicweb.org
'''

web = 'http://www.cubicweb.org/project/%s' % distname
ftp = ''

classifiers = [
    'Environment :: Web Environment',
    'Framework :: CubicWeb',
    'Programming Language :: Python',
    'Programming Language :: JavaScript',
    ]

pyversions = ['2.4']

__depends_cubes__ = {'addressbook': None}
__depends__ = {'cubicweb': '>= 3.6.0'}
for key, value in __depends_cubes__.items():
    __depends__['cubicweb-'+key] = value
__use__ = tuple(__depends_cubes__)

# packaging ###

from os import listdir as _listdir
from os.path import join, isdir
from glob import glob

CUBES_DIR = join('share', 'cubicweb', 'cubes')
THIS_CUBE_DIR = join(CUBES_DIR, 'company')

scripts = glob(join('bin', 'company-*'))

def listdir(dirpath):
    return [join(dirpath, fname) for fname in _listdir(dirpath)
            if fname[0] != '.' and not fname.endswith('.pyc')
            and not fname.endswith('~')]

try:
    data_files = [
        # common files
        [THIS_CUBE_DIR, [fname for fname in glob('*.py') if fname != 'setup.py']],
        # client (web) files
        [join(THIS_CUBE_DIR, 'i18n'),  listdir('i18n')],
        # Note: here, you'll need to add views' subdirectories if you want
        # them to be included in the debian package
        # server files
        [join(THIS_CUBE_DIR, 'migration'), listdir('migration')],
        [join(THIS_CUBE_DIR, 'views'), listdir('views')],
        ]
except OSError:
    # we are in an installed directory
    pass

cube_eid = None # <=== FIXME if you need direct bug-subscription

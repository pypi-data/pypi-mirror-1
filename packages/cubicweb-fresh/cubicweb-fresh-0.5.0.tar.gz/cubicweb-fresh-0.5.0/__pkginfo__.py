# pylint: disable-msg=W0622
"""cubicweb-fresh application packaging information"""

modname = 'fresh'
distname = 'cubicweb-fresh'

numversion = (0, 5, 0)
version = '.'.join(str(num) for num in numversion)

license = 'LGPL'
copyright = '''Copyright (c) 2008-2010 LOGILAB S.A. (Paris, FRANCE).
http://www.logilab.fr/ -- mailto:contact@logilab.fr'''

author = 'Logilab'
author_email = 'contact@logilab.fr'

short_desc = 'expense tracking application built on the CubicWeb framework'
long_desc = '''This CubicWeb component provides an expense tracking application.

CubicWeb is a semantic web application framework, see http://www.cubicweb.org
'''

ftp = ''
web = 'http://www.cubicweb.org/project/%s' % distname

classifiers = [
    'Environment :: Web Environment',
    'Framework :: CubicWeb',
    'Programming Language :: Python',
    'Programming Language :: JavaScript',
    ]

pyversions = ['2.4']

__depends_cubes__ = {'expense': '>= 0.4.4',
                     'workcase': None,
                     }
__depends__ = {'cubicweb': '>= 3.6.0'}
for key, value in __depends_cubes__.items():
    __depends__['cubicweb-'+key] = value
__use__ = tuple(__depends_cubes__)
__recommend__ = ()

# packaging ###

from glob import glob
from os import listdir as _listdir
from os.path import join, isdir

#from cubicweb.devtools.pkginfo import get_distutils_datafiles
TEMPLATES_DIR = join('share', 'cubicweb', 'cubes')
THIS_TEMPLATE_DIR = join(TEMPLATES_DIR, 'fresh')

def listdir(dirpath):
    return [join(dirpath, fname) for fname in _listdir(dirpath)
            if fname[0] != '.' and not fname.endswith('.pyc')
            and not fname.endswith('~')]

try:
    data_files = [
        [THIS_TEMPLATE_DIR, [fname for fname in glob('*.py') if fname != 'setup.py']],
        [join(THIS_TEMPLATE_DIR, 'i18n'),  listdir('i18n')],
        [join(THIS_TEMPLATE_DIR, 'views'), listdir('views')],
        [join(THIS_TEMPLATE_DIR, 'migration'), listdir('migration')],
        ]
except OSError:
    # we are in an installed directory
    pass

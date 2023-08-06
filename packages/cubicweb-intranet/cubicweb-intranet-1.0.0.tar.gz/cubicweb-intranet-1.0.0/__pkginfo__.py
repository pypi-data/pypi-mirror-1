# pylint: disable-msg=W0622
"""cubicweb-intranet application packaging information"""

modname = 'intranet'
distname = "cubicweb-intranet"

numversion = (1, 0, 0)
version = '.'.join(str(num) for num in numversion)

license = 'LGPL'
copyright = '''Copyright (c) 2003-2010 LOGILAB S.A. (Paris, FRANCE).
http://www.logilab.fr/ -- mailto:contact@logilab.fr'''

author = "Logilab"
author_email = "contact@logilab.fr"

short_desc = "an intranet built on the CubicWeb framework"
long_desc = """
CubicWeb is a semantic web application framework, see http://www.cubicweb.org
"""

web = 'http://cubicweb.org/project/cubicweb-intranet'
ftp = ''

pyversions = ['2.4']

classifiers = [
    'Environment :: Web Environment'
    'Framework :: CubicWeb',
    'Programming Language :: Python',
    'Programming Language :: JavaScript',
    ]

__depends_cubes__ = {'blog': None,
                     'book': None,
                     'card': None,
                     'comment': None,
                     'file': None,
                     'folder': None,
                     'link': None,
                     'tag': None,
                     'task': None,
                     'event': None,
                     }
__depends__ = {'cubicweb': '>= 3.6.0'}
for key, value in __depends_cubes__.items():
    __depends__['cubicweb-'+key] = value
__use__ = tuple(__depends_cubes__)
__recommend__ = ()

# packaging ###

from os import listdir
from os.path import join, isdir

TEMPLATES_DIR = join('share', 'cubicweb', 'cubes')
try:
    data_files = [
        [join(TEMPLATES_DIR, 'intranet'),
         [fname for fname in listdir('.')
          if fname.endswith('.py') and fname != 'setup.py']],
        [join(TEMPLATES_DIR, 'intranet', 'data'),
         [join('data', fname) for fname in listdir('data')]],
        [join(TEMPLATES_DIR, 'intranet', 'i18n'),
         [join('i18n', fname) for fname in listdir('i18n')]],
        [join(TEMPLATES_DIR, 'intranet', 'migration'),
         [join('migration', fname) for fname in listdir('migration')]],
        ]
except OSError:
    # we are in an installed directory
    pass

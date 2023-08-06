# pylint: disable-msg=W0622
"""cubicweb-intranet application packaging information"""

distname = "cubicweb-intranet"
modname = distname.split('-', 1)[1]

numversion = (0, 16, 0)
version = '.'.join(str(num) for num in numversion)

license = 'LCL'
copyright = '''Copyright (c) 2003-2009 LOGILAB S.A. (Paris, FRANCE).
http://www.logilab.fr/ -- mailto:contact@logilab.fr'''

author = "Logilab"
author_email = "contact@logilab.fr"

short_desc = "CubicWeb cube for intranets"
long_desc = """CubicWeb is a entities / relations bases knowledge management system
developed at Logilab.
.
This package provides the "Intranet" application built on top of CubicWeb.
It manages users, documents, links, tasks, events, etc.
"""

from os import listdir
from os.path import join, isdir

web = 'http://cubicweb.org/project/cubicweb-intranet'
ftp = ''

pyversions = ['2.4']

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

__use__ = ('blog', 'book', 'card', 'link', 'file', 'folder', 'tag', 'comment', 'task', 'event')
cube_eid = 8562

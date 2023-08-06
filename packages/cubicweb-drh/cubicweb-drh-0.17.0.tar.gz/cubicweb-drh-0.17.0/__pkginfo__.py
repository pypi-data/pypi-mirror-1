# pylint: disable-msg=W0622
"""cubicweb-drh packaging information"""

modname = 'drh'
distname = "cubicweb-drh"

numversion = (0, 17, 0)
version = '.'.join(str(num) for num in numversion)

license = 'LGPL'
copyright = '''Copyright (c) 2003-2010 LOGILAB S.A. (Paris, FRANCE).
http://www.logilab.fr/ -- mailto:contact@logilab.fr'''

author = "Logilab"
author_email = "contact@logilab.fr"

short_desc = "drh component for the CubicWeb framework"
long_desc = """This CubicWeb component provides an human resources management application
usable to manage a recruitment process.

CubicWeb is a semantic web application framework, see http://www.cubicweb.org
"""

ftp = ''
web = 'http://www.cubicweb.org/project/%s' % distname

classifiers = [
    'Environment :: Web Environment',
    'Framework :: CubicWeb',
    'Programming Language :: Python',
    'Programming Language :: JavaScript',
    ]

pyversions = ['2.4']

orig_dir = 'schemas'

__depends_cubes__ = {'file': None,
                     'email': None,
                     'person': None,
                     'addressbook': None,
                     'folder': None,
                     'tag': None,
                     'comment': None,
                     # could be moved out
                     'basket': None,
                     'event': None,
                     'task': None,
                     }
__depends__ = {'cubicweb': '>= 3.6.0'}
for key, value in __depends_cubes__.items():
    __depends__['cubicweb-'+key] = value
__use__ = tuple(__depends_cubes__)

from os import listdir
from os.path import join

TEMPLATES_DIR = join('share', 'cubicweb', 'cubes')
try:
    data_files = [
        [join(TEMPLATES_DIR, 'drh'),
         [fname for fname in listdir('.')
          if fname.endswith('.py') and fname != 'setup.py']],
        [join(TEMPLATES_DIR, 'drh', 'views'),
         [join('views', fname) for fname in listdir('views')]],
        [join(TEMPLATES_DIR, 'drh', 'i18n'),
         [join('i18n', fname) for fname in listdir('i18n')]],
        [join(TEMPLATES_DIR, 'drh', 'migration'),
         [join('migration', fname) for fname in listdir('migration')]],
        ]
except OSError:
    # we are in an installed directory
    pass

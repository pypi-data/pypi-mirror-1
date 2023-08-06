# pylint: disable-msg=W0622
"""cubicweb-file packaging information"""

modname = 'file'
distname = "cubicweb-file"

numversion = (1, 8, 0)
version = '.'.join(str(num) for num in numversion)

license = 'LGPL'
copyright = '''Copyright (c) 2003-2010 LOGILAB S.A. (Paris, FRANCE).
http://www.logilab.fr/ -- mailto:contact@logilab.fr'''

author = "Logilab"
author_email = "contact@logilab.fr"
web = 'http://www.cubicweb.org/project/%s' % distname

short_desc = "file component for the CubicWeb framework"
long_desc = """This CubicWeb component models files and images (pdf document,
word processor file, screenshots, etc).

CubicWeb is a semantic web framework, see http://www.cubicweb.org
"""

from os import listdir
from os.path import join

CUBES_DIR = join('share', 'cubicweb', 'cubes')
try:
    data_files = [
        [join(CUBES_DIR, 'file'),
         [fname for fname in listdir('.')
          if fname.endswith('.py') and fname != 'setup.py']],
        [join(CUBES_DIR, 'file', 'data'),
         [join('data', fname) for fname in listdir('data') if not fname == 'icons']],
        [join(CUBES_DIR, 'file', 'data', 'icons'),
         [join('data', 'icons', fname) for fname in listdir(join('data', 'icons'))]],
        [join(CUBES_DIR, 'file', 'wdoc'),
         [join('wdoc', fname) for fname in listdir('wdoc')]],
        [join(CUBES_DIR, 'file', 'views'),
         [join('views', fname) for fname in listdir('views') if fname.endswith('.py')]],
        [join(CUBES_DIR, 'file', 'i18n'),
         [join('i18n', fname) for fname in listdir('i18n')]],
        [join(CUBES_DIR, 'file', 'migration'),
         [join('migration', fname) for fname in listdir('migration')]],
        ]
except OSError:
    # we are in an installed directory
    pass


# used packages
__depends_cubes__ = {}
__depends__ = {'cubicweb': '>= 3.6.0',
               'PIL':None,
               }
__use__ = tuple(__depends_cubes__) # for bw compat with cw <= 3.4
classifiers = [
           'Environment :: Web Environment',
           'Framework :: CubicWeb',
           'Programming Language :: Python',
           'Programming Language :: JavaScript',
]

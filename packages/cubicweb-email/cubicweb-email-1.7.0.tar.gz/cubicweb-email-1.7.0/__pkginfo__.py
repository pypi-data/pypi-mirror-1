# pylint: disable-msg=W0622
"""cubicweb-email packaging information"""

modname = 'email'
distname = "cubicweb-%s" % modname

numversion = (1, 7, 0)
version = '.'.join(str(num) for num in numversion)

license = 'LGPL'
copyright = '''Copyright (c) 2003-2010 LOGILAB S.A. (Paris, FRANCE).
http://www.logilab.fr/ -- mailto:contact@logilab.fr'''

author = "Logilab"
author_email = "contact@logilab.fr"
web = 'http://www.cubicweb.org/project/%s' % distname

short_desc = "email component for the CubicWeb framework"
long_desc = """This CubicWeb component models email messages.

CubicWeb is a semantic web framework, see http://www.cubicweb.org
"""

from os import listdir
from os.path import join

CUBES_DIR = join('share', 'cubicweb', 'cubes')
try:
    data_files = [
        [join(CUBES_DIR, 'email'),
         [fname for fname in listdir('.')
          if fname.endswith('.py') and fname != 'setup.py']],
        [join(CUBES_DIR, 'email', 'views'),
         [join('views', fname) for fname in listdir('views')
          if not fname.endswith('.pyc')]],
        #[join(CUBES_DIR, 'email', 'data'),
        # [join('data', fname) for fname in listdir('data')]],
        [join(CUBES_DIR, 'email', 'i18n'),
         [join('i18n', fname) for fname in listdir('i18n')]],
        [join(CUBES_DIR, 'email', 'migration'),
         [join('migration', fname) for fname in listdir('migration')]],
        ]
except OSError:
    # we are in an installed directory
    pass

# used packages
__depends_cubes__ = {'file': '>= 1.6.0',}
__use__ = tuple(__depends_cubes__)
__depends__ = {'cubicweb': '>= 3.6.0'}
for key, value in __depends_cubes__.items():
    __depends__['cubicweb-'+key] = value
__recommend__ = ('comment',)
classifiers = [
           'Environment :: Web Environment',
           'Framework :: CubicWeb',
           'Programming Language :: Python',
           'Programming Language :: JavaScript',
]

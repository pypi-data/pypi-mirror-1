# pylint: disable-msg=W0622
"""cubicweb-zone packaging information"""

modname = 'zone'
distname = "cubicweb-%s" % modname

numversion = (1, 3, 0)
version = '.'.join([str(num) for num in numversion])

license = 'LGPL'
copyright = '''Copyright (c) 2003-2010 LOGILAB S.A. (Paris, FRANCE).
http://www.logilab.fr/ -- mailto:contact@logilab.fr'''

author = "Logilab"
author_email = "contact@logilab.fr"
web = 'http://www.cubicweb.org/project/%s' % distname

short_desc = "zone component for the CubicWeb framework"
long_desc = """This CubicWeb component models geographical zones (a city in a state
in a country is a zone in a zone in a zone).

CubicWeb is a semantic web framework, see http://www.cubicweb.org
"""

classifiers = [
    'Environment :: Web Environment',
    'Framework :: CubicWeb',
    'Programming Language :: Python',
    'Programming Language :: JavaScript',
    ]

# dependencies

__depends_cubes__ = {}
__depends__ = {'cubicweb': '>= 3.6.0'}
__use__ = tuple(__depends_cubes__)

# packaging

from os import listdir
from os.path import join

CUBES_DIR = join('share', 'cubicweb', 'cubes')
try:
    data_files = [
        [join(CUBES_DIR, 'zone'),
         [fname for fname in listdir('.')
          if fname.endswith('.py') and fname != 'setup.py']],
        [join(CUBES_DIR, 'zone', 'data'),
         [join('data', fname) for fname in listdir('data')]],
        [join(CUBES_DIR, 'zone', 'i18n'),
         [join('i18n', fname) for fname in listdir('i18n')]],
        [join(CUBES_DIR, 'zone', 'migration'),
         [join('migration', fname) for fname in listdir('migration')]],
        ]
except OSError:
    # we are in an installed directory
    pass

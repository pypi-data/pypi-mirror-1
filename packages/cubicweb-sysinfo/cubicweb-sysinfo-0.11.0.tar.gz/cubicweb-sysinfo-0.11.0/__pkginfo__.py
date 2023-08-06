# pylint: disable-msg=W0622
"""cubicweb-sysinfo packaging information"""

modname = 'sysinfo'
distname = "cubicweb-sysinfo"

numversion = (0, 11, 0)
version = '.'.join(str(num) for num in numversion)

license = 'LGPL'
copyright = '''Copyright (c) 2003-2010 LOGILAB S.A. (Paris, FRANCE).
http://www.logilab.fr/ -- mailto:contact@logilab.fr'''

author = "Logilab"
author_email = "contact@logilab.fr"

short_desc = "sysinfo component for the CubicWeb framework"
long_desc = """This CubicWeb component provides a computer inventory system
(to manage an inventory of computers, printers, keyboards, displays, etc).

CubicWeb is a semantic web application framework, see http://www.cubicweb.org
"""

web = 'http://www.cubicweb.org/project/%s' % distname

classifiers = [
    'Environment :: Web Environment',
    'Framework :: CubicWeb',
    'Programming Language :: Python',
    'Programming Language :: JavaScript',
    ]

# dependencies

__depends_cubes__ = {'zone': None,
                     'file': None,
                     'folder': None,
                     'comment': None,
                     'link': None,
                     'tag': None,
                     'vcsfile': None,
                     }
__depends__ = {'cubicweb': '>= 3.6.0'}
for key, value in __depends_cubes__.items():
    __depends__['cubicweb-'+key] = value
__use__ = tuple(__depends_cubes__)

# packaging

from os import listdir
from os.path import join, isdir
import glob

pyversions = ['2.4']

CUBES_DIR = join('share', 'cubicweb', 'cubes')
try:
    data_files = [
        # server / client python files
        [join(CUBES_DIR, 'sysinfo'),
         [fname for fname in listdir('.')
          if fname.endswith('.py') and fname != 'setup.py']],
        # modpython client files
        [join(CUBES_DIR, 'sysinfo', 'data'),
         [join('data', fname) for fname in listdir('data') if fname != 'CVS']],
        [join(CUBES_DIR, 'sysinfo', 'i18n'),
         [join('i18n', fname) for fname in listdir('i18n')
          if fname != 'CVS' and not isdir(join('i18n', fname))]],
        [join(CUBES_DIR, 'sysinfo', 'views'),
         [join('views', fname) for fname in listdir('views')
          if fname != 'CVS' and not fname.endswith('.pyc')]],
        # server files
        [join(CUBES_DIR, 'sysinfo', 'migration'),
         [join('migration', fname) for fname in listdir('migration')
          if fname != 'CVS']],
        ]
except OSError:
    # we are in an installed directory
    pass

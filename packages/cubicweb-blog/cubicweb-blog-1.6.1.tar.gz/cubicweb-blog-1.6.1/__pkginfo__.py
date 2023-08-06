# pylint: disable-msg=W0622
"""cubicweb-blog packaging information"""

distname = "cubicweb-blog"
modname = distname.split('-', 1)[1]

numversion = (1, 6, 1)
version = '.'.join(str(num) for num in numversion)

license = 'LGPL'
copyright = '''Copyright (c) 2003-2009 LOGILAB S.A. (Paris, FRANCE).
http://www.logilab.fr/ -- mailto:contact@logilab.fr'''

author = "Logilab"
author_email = "contact@logilab.fr"
web = ''

short_desc = "blog support for the CubicWeb framework"
long_desc = """CubicWeb is a entities / relations bases knowledge management system
developped at Logilab.
.
This package provides schema and views to add bloging functionalities to
cubicweb applications.
.
"""

from os import listdir
from os.path import join

CUBES_DIR = join('share', 'cubicweb', 'cubes')
try:
    data_files = [
        [join(CUBES_DIR, 'blog'),
         [fname for fname in listdir('.')
          if fname.endswith('.py') and fname != 'setup.py']],
        [join(CUBES_DIR, 'blog', 'data'),
         [join('data', fname) for fname in listdir('data')]],
        [join(CUBES_DIR, 'blog', 'i18n'),
         [join('i18n', fname) for fname in listdir('i18n')]],
        [join(CUBES_DIR, 'blog', 'migration'),
         [join('migration', fname) for fname in listdir('migration')]],
        ]
except OSError:
    # we are in an installed directory
    pass


cube_eid = 20300
# used packages
__use__ = ()

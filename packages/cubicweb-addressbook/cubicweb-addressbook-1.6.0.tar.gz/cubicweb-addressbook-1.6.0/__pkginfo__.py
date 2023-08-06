# pylint: disable-msg=W0622
"""cubicweb-addressbook packaging information"""

modname = 'addressbook'
distname = "cubicweb-%s" % modname

numversion = (1, 6, 0)
version = '.'.join(str(num) for num in numversion)

license = 'LGPL'
copyright = '''Copyright (c) 2003-2010 LOGILAB S.A. (Paris, FRANCE).
http://www.logilab.fr/ -- mailto:contact@logilab.fr'''

author = "Logilab"
author_email = "contact@logilab.fr"

web = 'http://www.cubicweb.org/project/%s' % distname
ftp = ''

short_desc = "address book component for the CubicWeb framework"
long_desc = """\
Summary
-------

The addressbook cube adds a phone number, postal address and instant
messenger address (supports icq, msn and jabber) to the schema.

Views description
-----------------
There's only basic entity views in there.
"""
web = 'http://www.cubicweb.org/project/%s' % distname

classifiers = [
    'Environment :: Web Environment',
    'Framework :: CubicWeb',
    'Programming Language :: Python',
    'Programming Language :: JavaScript',
    ]


__depends_cubes__ = {}
__depends__ = {'cubicweb': '>= 3.6.0'}
__use__ = tuple(__depends_cubes__)

pyversions = ['2.4']

# packages ###

from os import listdir
from os.path import join

CUBES_DIR = join('share', 'cubicweb', 'cubes')
try:
    data_files = [
        [join(CUBES_DIR, 'addressbook'),
         [fname for fname in listdir('.')
          if fname.endswith('.py') and fname != 'setup.py']],
        [join(CUBES_DIR, 'addressbook', 'i18n'),
         [join('i18n', fname) for fname in listdir('i18n')]],
        [join(CUBES_DIR, 'addressbook', 'schema'),
         [join('schema', fname) for fname in listdir('schema')]],
        [join(CUBES_DIR, 'addressbook', 'migration'),
         [join('migration', fname) for fname in listdir('migration')]],
        ]
except OSError:
    # we are in an installed directory
    pass

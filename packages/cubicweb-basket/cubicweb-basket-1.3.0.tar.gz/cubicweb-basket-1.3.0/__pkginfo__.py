# pylint: disable-msg=W0622
"""cubicweb-basket packaging information"""

modname = 'basket'
distname = "cubicweb-%s" % modname

numversion = (1, 3, 0)
version = '.'.join(str(num) for num in numversion)

license = 'LGPL'
copyright = '''Copyright (c) 2003-2010 LOGILAB S.A. (Paris, FRANCE).
http://www.logilab.fr/ -- mailto:contact@logilab.fr'''

author = "Logilab"
author_email = "contact@logilab.fr"
web = 'http://www.cubicweb.org/project/%s' % distname

short_desc = "shopping cart component for the CubicWeb framework"
long_desc = """\
Summary
-------

This cube provides a shopping cart functionality.

Usage
-----

By default, any entity can be added to a basket (this uses the
`in_basket` relation).

There is a box that displays all items in the basket. By default, this
box is hidden. To display it, add in a view this code:

.. sourcecode:: python

   from cubes.basket.views import BasketBox

   BasketBox.visible = True

"""

classifiers = [
    'Environment :: Web Environment',
    'Framework :: CubicWeb',
    'Programming Language :: Python',
    'Programming Language :: JavaScript',
    ]

__depends_cubes__ = {}
__depends__ = {'cubicweb': '>= 3.6.0'}
__use__ = ()

# packaging ###

from os import listdir
from os.path import join

CUBES_DIR = join('share', 'cubicweb', 'cubes')
try:
    data_files = [
        [join(CUBES_DIR, 'basket'),
         [fname for fname in listdir('.')
          if fname.endswith('.py') and fname != 'setup.py']],
        [join(CUBES_DIR, 'basket', 'data'),
         [join('data', fname) for fname in listdir('data')]],
        [join(CUBES_DIR, 'basket', 'i18n'),
         [join('i18n', fname) for fname in listdir('i18n')]],
        [join(CUBES_DIR, 'basket', 'migration'),
         [join('migration', fname) for fname in listdir('migration')]],
        ]
except OSError, ex:
    # we are in an installed directory
    pass


template_eid = 20279

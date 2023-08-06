# pylint: disable-msg=W0622
"""cubicweb-classification-schemes packaging information"""

modname = 'keyword'
distname = "cubicweb-keyword"

numversion = (1, 6, 0)
version = '.'.join(str(num) for num in numversion)

license = 'LGPL'
copyright = '''Copyright (c) 2003-2010 LOGILAB S.A. (Paris, FRANCE).
http://www.logilab.fr/ -- mailto:contact@logilab.fr'''

author = "Logilab"
author_email = "contact@logilab.fr"
web = 'http://www.cubicweb.org/project/%s' % distname

short_desc = "keyword component for the Cubicweb framework"
long_desc = """Summary
-------
The `keyword` cube provides classification by using hierarchies of keywords to
classify content.

There is two types of keywords:

- `Keyword` which contains a description,
- `CodeKeyword` which contains the keyword description and the
  associated code.

In order to link an entity to a keyword, you have to add a relation
`applied_to` in the schema.

Each keyword has the `subkeyword_of` relation definition. This allows
to navigate in the classification without a Modified Preorder Tree
Traversal representation of the data.

Some methods are defined in order to get parents and children or get
the status of a keyword (leaf or root).

See also cubicweb-tag as another (simpler) way to classify content.
"""

classifiers = [
    'Environment :: Web Environment',
    'Framework :: CubicWeb',
    'Programming Language :: Python',
    'Programming Language :: JavaScript',
    ]

__depends_cubes__ = {}
__depends__ = {'cubicweb': '>= 3.6.0'}
__use__ = tuple(__depends_cubes__)

from os import listdir
from os.path import join

CUBES_DIR = join('share', 'cubicweb', 'cubes')
try:
    data_files = [
        [join(CUBES_DIR, 'keyword'),
         [fname for fname in listdir('.')
          if fname.endswith('.py') and fname != 'setup.py']],
        [join(CUBES_DIR, 'keyword', 'data'),
         [join('data', fname) for fname in listdir('data')]],
        [join(CUBES_DIR, 'keyword', 'i18n'),
         [join('i18n', fname) for fname in listdir('i18n')]],
        [join(CUBES_DIR, 'keyword', 'migration'),
         [join('migration', fname) for fname in listdir('migration')]],
        ]
except OSError:
    # we are in an installed directory
    pass

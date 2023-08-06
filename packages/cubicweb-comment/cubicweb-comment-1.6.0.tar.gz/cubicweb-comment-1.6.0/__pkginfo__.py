# pylint: disable-msg=W0622
"""cubicweb-comment packaging information"""

modname = 'comment'
distname = "cubicweb-%s" % modname

numversion = (1, 6, 0)
version = '.'.join(str(num) for num in numversion)

license = 'LGPL'
copyright = '''Copyright (c) 2003-2010 LOGILAB S.A. (Paris, FRANCE).
http://www.logilab.fr/ -- mailto:contact@logilab.fr'''

author = "Logilab"
author_email = "contact@logilab.fr"
web = 'http://www.cubicweb.org/project/%s' % distname

short_desc = "comment component for the CubicWeb framework"
long_desc = """\
Summary
-------

The `comment` cube provides threadable comments feature.

Usage
-----

This cube creates a new entity type called `Comment` which could basically be
read by every body but only added by application's users.
It also defines a relation `comments` which provides the ability to add a
`Comment` which `comments` a `Comment`.

To use this cube, you want to add the relation `comments` on the entity type
you want to be able to comment. For instance, let's say your cube defines a
schema for a blog. You want all the blog entries to be commentable.
Here is how to define it in your schema:

.. sourcecode:: python

    from yams.buildobjs import RelationDefinition
    class comments(RelationDefinition):
        subject = 'Comment'
        object = 'BlogEntry'
        cardinality = '1*'

Once this relation is defined, you can post comments and view threadable
comments automatically on blog entry's primary view.
"""

from os import listdir
from os.path import join

CUBES_DIR = join('share', 'cubicweb', 'cubes')

try:
    data_files = [
        [join(CUBES_DIR, 'comment'),
         [fname for fname in listdir('.')
          if fname.endswith('.py') and fname != 'setup.py']],
        [join(CUBES_DIR, 'comment', 'data'),
         [join('data', fname) for fname in listdir('data')]],
        [join(CUBES_DIR, 'comment', 'i18n'),
         [join('i18n', fname) for fname in listdir('i18n')]],
        [join(CUBES_DIR, 'comment', 'migration'),
         [join('migration', fname) for fname in listdir('migration')]],
        ]
except OSError:
    # we are in an installed directory
    pass


cube_eid = 20316
# used packages
__depends_cubes__ = {}
__depends__ = {'cubicweb': '>= 3.6.0'}
__use__ = tuple(__depends_cubes__)
classifiers = [
           'Environment :: Web Environment',
           'Framework :: CubicWeb',
           'Programming Language :: Python',
           'Programming Language :: JavaScript',
]

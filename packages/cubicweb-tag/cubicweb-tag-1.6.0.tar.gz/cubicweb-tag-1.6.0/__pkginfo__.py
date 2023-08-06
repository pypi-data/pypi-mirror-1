# pylint: disable-msg=W0622
"""cubicweb-tag packaging information"""

modname = 'tag'
distname = "cubicweb-%s" % modname

numversion = (1, 6, 0)
version = '.'.join(str(num) for num in numversion)

license = 'LGPL'
copyright = '''Copyright (c) 2003-2010 LOGILAB S.A. (Paris, FRANCE).
http://www.logilab.fr/ -- mailto:contact@logilab.fr'''

author = "Logilab"
author_email = "contact@logilab.fr"
web = 'http://www.cubicweb.org/project/%s' % distname

short_desc = "tag component for the CubicWeb framework"
long_desc = """\
Summary
-------

The tag cube allows to add labels to an entity as a simple yet powerful way to
classify your content. Tags can be used to raffinate a for search using facets.

Usage
-----

To allow tags on an entity type, you must allow the `tags` relation between `Tag`
and you entity type(s).

For instance to activate the tag functionnality on Person, Company and Division
entity type, one should add to his schema:

.. sourcecode:: python

   from yams.buildobjs import RelationDefinition
   class tags(RelationDefinition):
       subject = 'Tag'
       object = ('Person', 'Company', 'Division')

You should then see the tags box appearing on the primary view for entities of
those type. The`TagsBox` display tags applied to the entity but also provides
an easily way to add / remove tags, if you've the permission to do so.

More views
----------
- The `SimilarEntitiesBox` shows some entities which share the most tags together

- The `TagsCloudView`, a classical, displaying a set of tags appearing more or
  less big according to the number of tagged entities. It's used by the
  `TagsCouldBox`, which is not visible by default (user can activate it using
  their preferences)  but that you can activate by default using the code snippet below:

  .. sourcecode:: python

    from cubes.tag.views import TagsCloudBox
    # make the tags cloud box visible by default
    TagsCloudBox.visible = True

- The primary view for tags provides a tags merging interface to site administrators,
  very useful to manage tags on a site where people tend to express the same thing with
  different words, or spelling.
"""

from os import listdir
from os.path import join

CUBES_DIR = join('share', 'cubicweb', 'cubes')
try:
    data_files = [
        [join(CUBES_DIR, 'tag'),
         [fname for fname in listdir('.')
          if fname.endswith('.py') and fname != 'setup.py']],
        [join(CUBES_DIR, 'tag', 'data'),
         [join('data', fname) for fname in listdir('data')]],
        [join(CUBES_DIR, 'tag', 'wdoc'),
         [join('wdoc', fname) for fname in listdir('wdoc')]],
        [join(CUBES_DIR, 'tag', 'i18n'),
         [join('i18n', fname) for fname in listdir('i18n')]],
        [join(CUBES_DIR, 'tag', 'migration'),
         [join('migration', fname) for fname in listdir('migration')]],
        ]
except OSError:
    # we are in an installed directory
    pass

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

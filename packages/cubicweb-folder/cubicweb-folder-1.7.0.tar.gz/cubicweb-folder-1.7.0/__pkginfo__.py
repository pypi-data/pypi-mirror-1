# pylint: disable-msg=W0622
"""cubicweb-classification-folder packaging information"""

modname = 'folder'
distname = "cubicweb-folder"

numversion = (1, 7, 0)
version = '.'.join(str(num) for num in numversion)

license = 'LGPL'
copyright = '''Copyright (c) 2003-2010 LOGILAB S.A. (Paris, FRANCE).
http://www.logilab.fr/ -- mailto:contact@logilab.fr'''

author = "Logilab"
author_email = "contact@logilab.fr"
web = 'http://www.cubicweb.org/project/%s' % distname

short_desc = "folder component for the CubicWeb framework"
long_desc = """\
Summary
-------
The `folder` cube allows to create a tree of categories and classify entities
as you're used to do in a file-system.

Usage
-----

Define the relation `filed_under` in the schema, object must
contain all entities which can be classified in a folder.

.. sourcecode:: python

  class missing_filed_under(RelationDefinition):
      name = 'filed_under'
      subject = ('ExtProject', 'Project', 'Card', 'File')
      object = 'Folder'


The `FoldersBox` shows the folders hierarchy as a tree view. It's not visible by
default (user can activate it using their preferences) but you can activate it
by default using the code snippet below:

.. sourcecode:: python

    from cubes.folder.views import FoldersBox
    # make the folders box visible by default
    FoldersBox.visible = True
"""

from os import listdir
from os.path import join


CUBES_DIR = join('share', 'cubicweb', 'cubes')
try:
    data_files = [
        [join(CUBES_DIR, 'folder'),
         [fname for fname in listdir('.')
          if fname.endswith('.py') and fname != 'setup.py']],
        [join(CUBES_DIR, 'folder', 'data'),
         [join('data', fname) for fname in listdir('data')]],
        [join(CUBES_DIR, 'folder', 'i18n'),
         [join('i18n', fname) for fname in listdir('i18n')]],
        [join(CUBES_DIR, 'folder', 'migration'),
         [join('migration', fname) for fname in listdir('migration')]],
        ]
except OSError:
    # we are in an installed directory
    pass


__depends_cubes__ = {}
__depends__ = {'cubicweb': '>= 3.6.0'}
__use__ = tuple(__depends_cubes__)

classifiers = [
           'Environment :: Web Environment',
           'Framework :: CubicWeb',
           'Programming Language :: Python',
           'Programming Language :: JavaScript',
           ]


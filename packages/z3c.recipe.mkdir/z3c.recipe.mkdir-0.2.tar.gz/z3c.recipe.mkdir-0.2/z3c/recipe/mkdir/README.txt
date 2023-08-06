Detailed Description
********************

.. contents::


Recipe Options
==============

``z3c.recipe.mkdir`` provides the following options:

* ``path``
    Contains the path(s) of directories created in normalized,
    absolute form. I.e.:: 

      mydir/../foo/bar

    becomes

      /path/to/buildout-dir/foo/bar


Simple creation of directories via buildout
===========================================

Lets create a minimal `buildout.cfg` file::

  >>> write('buildout.cfg',
  ... '''
  ... [buildout]
  ... parts = mydir
  ... offline = true
  ...
  ... [mydir]
  ... recipe = z3c.recipe.mkdir
  ... ''')

Now we can run buildout::

  >>> print system(join('bin', 'buildout')),
  Installing mydir.

The directory was indeed created in the ``parts`` directory::

  >>> ls('parts')
  d  mydir

As we did not specify a special path, the name of the created
directory is like the section name ``mydir``.


Creating a directory in a given path
====================================

Lets create a minimal `buildout.cfg` file. This time the directory
has a name different from section name and we have to tell explicitly,
that we want it to be created in the ``parts/`` directory. We set the
``path`` option to do so:

  >>> write('buildout.cfg',
  ... '''
  ... [buildout]
  ... parts = mydir
  ... offline = true
  ...
  ... [mydir]
  ... recipe = z3c.recipe.mkdir
  ... path = ${buildout:parts-directory}/myotherdir
  ... ''')

Now we can run buildout::

  >>> print system(join('bin', 'buildout')),
  Uninstalling mydir.
  Installing mydir.

The directory was indeed created::

  >>> ls('parts')
  d  myotherdir


Creating relative paths
=======================

If we specify a relative path, this path will be read relative to the
buildout directory:

  >>> write('buildout.cfg',
  ... '''
  ... [buildout]
  ... parts = mydir
  ... offline = true
  ...
  ... [mydir]
  ... recipe = z3c.recipe.mkdir
  ... path = myrootdir
  ... ''')

  >>> print system(join('bin', 'buildout')),
  Uninstalling mydir.
  Installing mydir.

  >>> ls('.')
  -  .installed.cfg
  d  bin
  -  buildout.cfg
  d  develop-eggs
  d  eggs
  d  myrootdir
  d  parts

  The old directory will vanish:

  >>> ls('parts') is None
  True


Creating intermediate paths
===========================

If we specify several levels of directories, the intermediate parts
will be created for us as well:

  >>> write('buildout.cfg',
  ... '''
  ... [buildout]
  ... parts = mydir
  ... offline = true
  ...
  ... [mydir]
  ... recipe = z3c.recipe.mkdir
  ... path = myrootdir/other/dir/finaldir
  ... ''')

  >>> print system(join('bin', 'buildout')),
  Uninstalling mydir.
  Installing mydir.

  >>> ls('myrootdir', 'other', 'dir')
  d  finaldir


Paths are normalized
====================

If we specify a non-normalized path (i.e. one that contains references
to parent directories or similar), the path will be normalized before
creating it:

  >>> write('buildout.cfg',
  ... '''
  ... [buildout]
  ... parts = mydir
  ... offline = true
  ...
  ... [mydir]
  ... recipe = z3c.recipe.mkdir
  ... path = myroot/foo/../dir1/../bar/.
  ... ''')

  >>> print system(join('bin', 'buildout')),
  Uninstalling mydir.
  Installing mydir.

Only ``bar/`` will be created:

  >>> ls('myroot')
  d  bar


Creating multiple paths in a row
================================

We can create multiple paths in one buildout section:

  >>> write('buildout.cfg',
  ... '''
  ... [buildout]
  ... parts = mydir
  ... offline = true
  ...
  ... [mydir]
  ... recipe = z3c.recipe.mkdir
  ... path = myroot/dir1
  ...        myroot/dir2
  ... ''')

  >>> print system(join('bin', 'buildout')),
  Uninstalling mydir.
  Installing mydir.

  >>> ls('myroot')
  d  dir1
  d  dir2

Note, that in this case you cannot easily reference the set path from
other recipes or templates. If, for example in a template you
reference::

  root_dir = ${mydir:path}

the result will become::

  root_dir = /path/to/buildout/dir1
  path/to/buildout/dir2

If you specify only one path, however, the second line will not appear.

Use several sections using `z3c.recipe.mkdir` if you want to reference
different created paths from templates or similar.


Trailing slashes do not matter
==============================

It doesn't matter, whether you specify the paths with trailing slash
or without:

  >>> write('buildout.cfg',
  ... '''
  ... [buildout]
  ... parts = mydir
  ... offline = true
  ...
  ... [mydir]
  ... recipe = z3c.recipe.mkdir
  ... path = myroot/dir3/
  ...        myroot/dir4
  ... ''')

  >>> print system(join('bin', 'buildout')),
  Uninstalling mydir.
  Installing mydir.

  >>> ls('myroot')
  d  dir3
  d  dir4

Things to be aware of
=====================

If you change the setting of some path, the old directory and all its
contents will be lost:

  >>> write('buildout.cfg',
  ... '''
  ... [buildout]
  ... parts = mydir
  ... offline = true
  ...
  ... [mydir]
  ... recipe = z3c.recipe.mkdir
  ... path = path1
  ... ''')

  >>> print system(join('bin', 'buildout')),
  Uninstalling mydir.
  Installing mydir.

  >>> write(join('path1', 'myfile'), 'blah\n')
  >>> ls('path1')
  -  myfile

Now we switch the setting of mydir to ``path2``:

  >>> write('buildout.cfg',
  ... '''
  ... [buildout]
  ... parts = mydir
  ... offline = true
  ...
  ... [mydir]
  ... recipe = z3c.recipe.mkdir
  ... path = path2
  ... ''')

  >>> print system(join('bin', 'buildout'))
  Uninstalling mydir.
  Installing mydir.
  <BLANKLINE>

  >>> ls('path1')
  Traceback (most recent call last):
  OSError: [Errno ...] No such file or directory: 'path1'


Things, one should not do
=========================

If the path given already contains a file, an error is raised:

  >>> write('buildout.cfg',
  ... '''
  ... [buildout]
  ... parts = mydir
  ... offline = true
  ...
  ... [mydir]
  ... recipe = z3c.recipe.mkdir
  ... path = myrootdir/somefile/foo
  ... ''')

Now we create the first part of the path beforehand:

  >>> import os
  >>> os.mkdir('myrootdir')

And make the second part of the path a file:

  >>> write(join('myrootdir', 'somefile'),
  ... '''
  ... blah
  ... ''')

  >>> print system(join('bin', 'buildout')),
  Uninstalling mydir.
  Installing mydir.
  While:
    Installing mydir.
  Error: Cannot create directory: /.../myrootdir/somefile. It's a file.

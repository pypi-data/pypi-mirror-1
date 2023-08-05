
Setuptools_git Manual
=====================

About
-----

This is a plugin for setuptools that enables Git integration.  Once
installed, Setuptools can be told to include in a module distribution
all the files tracked by git.  This is an alternative to explicit
inclusion specifications with `MANIFEST.in`.

A module distribution here refers to a package that you create
throught setup.py, ex:

  python setup.py sdist
  python setup.py bdist_rpm
  python setup.py bdist_egg

This package was formerly known as gitlsfiles.  The name change is the
result of an effort by the setuptools plugin developers to provide a
uniform naming convention.


Installation
------------

With easy_install:

  easy_install setuptools_git

Alternative manual installation:

  tar -zxvf setuptools_git.X.Y.Z.tar.gz
  cd setuptools_git.X.Y.Z
  python setup.py install

Where X.Y.Z is a version number.



Usage
-----

To activate this plugin, you must first package your python module
with `setup.py` and use setuptools.  The former is well documented in
the distutils manual:

  http://docs.python.org/dist/dist.html

To use setuptools instead of distutils, just edit `setup.py` and
change

  from distutils.core import setup

to
  
  from setuptools import setup

By default, setuptools will not include files tracked by your revision
control system.  To enable this option, edit your `setup()` directive:

  setup(...,
    include_package_data=True, 
    ...)

This will include add the files tracked by a revision control system
that setuptools knows about.  This plugin provides support for git and
setuptools ships with support for cvs and subversion.

It might happen that you track files with your revision control system
and that you don't want to include those in your packages.  In that
case, you can prevent setuptools from packaging those files with a
directive in your `MANIFEST.in`, ex:

  exclude .gitignore
  recursive-exclude images *.xcf *.blend

In this example, we prevent setuptools from package `.gitignore` and
the Gimp and Blender source files found under the `images` directory.

Files to exclude from the package can also be listed in the `setup()`
directive:

  setup(...,
    exclude_package_data = {'': ['.gitignore'], 
    			    'images': ['*.xcf', '*.blend']},
    ...)


Gotchas
-------

Be aware that for this module to work properly, git and the git
meta-data must be available.  That means that if someone tries to make
a package distribution out of a non-git distribution of yours, say a
tarball, setuptools will lack the information necessary to know which
files to include.  A similar problem will happen if someone clones
your git repository but does not install this plugin.

Resolving those problems is out of the scope of this plugin; you
should add relevant warnings to your documentation if those situations
are a concern to you.


References
----------

How to distribute Python modules with Distutils:
  
  http://docs.python.org/dist/dist.html


Setuptools complete manual:

  http://peak.telecommunity.com/DevCenter/setuptools



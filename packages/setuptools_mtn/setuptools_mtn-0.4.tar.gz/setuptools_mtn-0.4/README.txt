setuptools_mtn Manual
=====================

About
-----

This is a plugin for setuptools that enables Monotone integration.
Once installed, setuptools can be told to include all the files
tracked by Monotone in a distribution.  This is an alternative to
explicit inclusion specifications with `MANIFEST.in`.

A "distribution" here refers to a package that you create using
setup.py.  For example, any of these commands create a distribution:

  python setup.py sdist
  python setup.py bdist_egg
  python setup.py bdist_rpm

Please send questions, comments, or patches to Dale Sedivec
<dale@codefu.org>.


Installation
------------

With easy_install:

  easy_install setuptools_mtn

Alternative manual installation:

  tar -zxvf setuptools_mtn-X.Y.Z.tar.gz
  cd setuptools_mtn-X.Y.Z
  python setup.py install

Where X.Y.Z is a version number.


Usage
-----

To activate this plugin for your Python module, you must first package
your module using `setup.py` and setuptools.  The former is well
documented in the distutils manual:

  http://docs.python.org/dist/dist.html

To use setuptools instead of distutils, just edit `setup.py` and
change

  from distutils.core import setup

to
 
  from setuptools import setup

When setuptools builds a source distribution it always includes all
files tracked by your revision control system--if it knows how to ask
what those files are.

When setuptools builds a binary distribution you can ask it to include
all files tracked by your revision control system by adding this
argument to your invocation of `setup()`:

  setup(...,
    include_package_data=True,
    ...)

setuptools_mtn lets setuptools know what files are tracked by your
Monotone revision control tool.  setuptools ships with support for CVS
and Subversion.  Other plugins like this one are available for Bazaar,
Git, Monotone, and Mercurial; you can find these (and maybe some new
ones) at the Python Package Index:

  http://pypi.python.org/

It might happen that you track files with your revision control system
that you don't want to include in your packages.  In that case, you
can prevent setuptools from packaging those files with a directive in
your `MANIFEST.in`.  For example:

  exclude .darcs-boringfile
  recursive-exclude images *.xcf *.blend

In this example, we prevent setuptools from packaging
`.darcs-boringfile` and the Gimp (`*.xcf`) and Blender (`*.blend`)
source files found under the `images` directory.

Alternatively, files to exclude from the package can be listed in the
`setup()` directive:

  setup(...,
    exclude_package_data = {'': ['.darcs-boringfile'],
    			    'images': ['*.xcf', '*.blend']},
    ...)


Gotchas
-------

If someone clones your Monotone repository and tries to build a
distribution without first installing this plugin, it is likely they
will be missing some of the files necessary for the distribution.  On
the other hand if someone gets a source distribution that was created
by `./setup.py sdist`, then it will come with a list of all files to
be included, so they will not need Monotone in order to build a
distribution themselves.

You can make sure that anyone who uses your setup.py file has this
plugin by adding a `setup_requires` argument:

  setup_requires=[]
  # The setuptools_mtn package is required to produce complete
  # distributions (such as with "sdist" or "bdist_egg"), unless there
  # is a PKG-INFO file present which contains the complete list of the
  # required files.
  # http://pypi.python.org/pypi/setuptools_mtn
  setup_requires.append('setuptools_mtn >= 1.0.5')

  setup(...,
    setup_requires = setup_requires,
    ...)


References
----------

How to distribute Python modules with distutils:
 
  http://docs.python.org/dist/dist.html


Setuptools complete manual:

  http://peak.telecommunity.com/DevCenter/setuptools


Thanks to Yannick Gingras and zooko for providing the prototype for
this README.txt and giving permission to copy it; nearly all of this
file is yanked directly from their work.

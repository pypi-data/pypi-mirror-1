
ulif.plone.testsetup
********************

is a package that provides some convenience stuff to enable rapid test
setup for Plone packages. Currently doctests (normal unit doctests and
functional doctests) and usual Python tests made of
``unittest.TestCase`` (and derived) definitions are supported.

Doctests and test modules are found throughout a whole package and
registered with sensible, modifiable defaults.

Also support for reusable test setups is provided by so-called
TestGetters and TestCollectors.

Setting up doctests (contrary to *writing* those tests) can become
cumbersome with Plone. In the environment you often have to prepare
complex things like test layers, setup functions, teardown functions
and much more. Often this steps have to be done again and again.

``ulif.plone.testsetup`` can shorten this work by setting sensible
defaults for the most important aspects of test setups.

See `README.txt` in the ``src/ulif/plone/testsetup`` directory for API
documentation. ``ulif.plone.testsetup`` is an extension of the Zope 3
package `z3c.testsetup
<http://cheeseshop.python.org/pypi/z3c.testsetup>`_ in which all the
basic stuff is defined and documented. Please see the .txt files in
this package for deeper insights about TestCollectors and the like.

Note, that this is alphaware! Do not use it in productive
environments!



Prerequisites
=============

You need::

- Python 2.4. Rumors are, that also Python 2.5 will do.

- `setuptools`, available from 
  http://peak.telecommunity.com/DevCenter/setuptools

Other needed packages will be downloaded during
installation. Therefore you need an internet connection during
installation. 


Installation
============

From the root of the package run::

     $ python2.4 bootstrap/bootstrap.py

This will download and install everything to run `buildout` in the
next step. Afterwards an executable script `buildout` should be
available in the freshly created `bin/` directory.

Next, fetch all needed packages, install them and create provided
scripts::

     $ bin/buildout

This should create an `instance` script in `bin/`.

Running::

     $ bin/instance test -s ulif.plone.testsetup

you can test the installed package.


Usage
=====

See `README.txt` and the other .txt files in the
``src/ulif/plone/testsetup`` directory for API documentation.



ulif.plone.testsetup
********************

A package for easier test setups with Plone 3.

``ulif.plone.testsetup`` tries to ease the writing of testsetups. This
can be a mess, especially when using Plone. There is always a complex
framework to setup and all that might afraid people so that they do
not write tests at all. In that sense, ``ulif.plone.testsetup`` is a
try to take away excuses for not testing.

Note, that this package is meant for use with Plone 3. Other versions
are not tested! 

Please note also, that this document is *not* an introduction into
writing tests, but into *setup* of tests. The difference is, that the
many kind of tests supported by Zope and Python need to be found by a
testrunner and some, functional tests for example, need a special
framework to be setup before the tests can actually run. That's what
this package is for: minimizing the effort, to find and setup tests.

A Simple Test Setup
===================

Setting up a test with this package in the minimal form comes down to
this::

   >>> from ulif.plone.testsetup import register_all_plone_tests
   >>> test_suite = register_all_plone_tests(
   ...    'ulif.plone.testsetup.tests.cave')

This will find all tests registered in the ``cave`` package and
deliver them to a testrunner when called. All we have to do, is to get
the ``register_all_plone_tests`` function and to pass it a package.

We specified the package to be searched for tests by a so-called
dotted name, but we can also pass the real package::

   >>> from ulif.plone.testsetup.tests import cave
   >>> test_suite = register_all_plone_tests(cave)

In both cases we will get a ``PloneTestCollector``::

   >>> test_suite
   <ulif.plone.testsetup.plonetesting.PloneTestCollector object at 0x...>

When called, it will return a test suite::

   >>> test_suite()
   <unittest.TestSuite tests=[...]>



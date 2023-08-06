
What is svnhelper ?
===================

This package provide some svn utils.


Import
======

When you importing a package for the first time, you need to create the
trunk/branches/tags tree, remove pyc files, .egg-info, etc.
svnhelper do it for you.

In a python package, just use::

  $ python setup.py import

And you will be prompted for the repository root. Do not add the package name
in the url. The name will be retrieved from the current path.

Outside a python package, you can use this command line::

  $ svnh -i <repository>

Checkout
========

To checkout a package, use::

  $ svnco <url>

If no branche or tag is found in the url. svnhelper will checkout the trunk.

Testing
=======

It's not easy to test svn stuff in unit tests. svnhelper provide a testing
environment for you.

Here is how to create a temporary repository::

  >>> from svnhelper.testing import setUpRepository
  >>> from svnhelper.testing import tearDownRepository

  >>> def setUp(test):
  ...     setUpRepository(test)

  >>> def tearDown(test):
  ...     tearDownRepository(test)

Then you can import a directory in the repository. test_package is a directory
pointing on a testing egg in the test/ directory::

  >>> import_test_package(test_package)  

The we can use the repository::

  >>> dirname = create_tempdir()
  >>> os.chdir(dirname)
  >>> print svn('co', '%s/my.testing/trunk' % repository, 'my.testing')
  A    my.testing/LICENSE
  A    my.testing/my
  A    my.testing/my/__init__.py
  A    my.testing/my/testing
  A    my.testing/my/testing/__init__.py
  A    my.testing/my/testing/README.txt
  A    my.testing/setup.py
  Checked out revision 1.

  >>> ls(dirname, 'my.testing')
  d .svn
  - LICENSE
  d my
  - setup.py




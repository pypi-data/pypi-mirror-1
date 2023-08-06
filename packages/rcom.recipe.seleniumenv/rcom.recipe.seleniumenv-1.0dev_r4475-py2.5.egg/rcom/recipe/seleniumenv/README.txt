Supported options
=================

The recipe supports the following options:

seleniumversion
    The version of selenium to use, the version numbers can be taken from
    http://release.seleniumhq.org/selenium-remote-control/. Default: nightlyBuild.

eggs
    The eggs to include in the runner path. Any product included in the path will be
    accesible for the runner to search and run selenium tests from.

java-cmd
    The commando used to run the selenium server. Default: java.

Example usage
=============

The basic buildout that uses the recipe should look like the following::

    >>> write('buildout.cfg',
    ... """
    ... [buildout]
    ... parts = seleniumenv
    ...
    ... [seleniumenv]
    ... recipe = rcom.recipe.seleniumenv
    ... seleniumversion = 1.0-beta-2
    ... eggs = ${instance:eggs}


The seleniumrunner script
=========================

The selenium runner is a scipt to find and run **selenium tests**, it will
be on your bin directory once the recipe is instanlled
It receives different parameters and it's main objective is to simplify the
tests execution and reporting procedure.
This script will wake-up the selenium RC server, search and run the tests
and then shutdown the server and report the tests result.
Once the recipe has been installed, a tests runner should be placed on the bin directory

Running the tests
-----------------

To run the suite of tests buldled with any product, the first thing to do after
the buildout has been run is to prepare a Plone site to test (if the user doesn't
have a Plone site to test, yet).
For this to be done, you must first wake up the instance::

    ./bin/instance start

To run all the selenium tests for a product the user should pass at least two
parameters:

-i instance
        The Plone site's name.

-s product
        The product in which the runner will search for tests to run.

An example test execution will be::

        $ ./bin/seleniumrunner -i testPloneSite -s namespace.product

This will search all the **selenium** tests for the product and run them
on http://localhost:<port_used>/testPloneSite.

For running  a particular test, the -t parameter should be passed to the runner::

        $ ./bin/seleniumrunner -i testPloneSite -s namespace.product -t exampleTest

.. Note::

    Please notice that the exampleTest.py test should be stored in the
    respective location and added to the __init__py file (See `Creating a test`_)

Creating a test
---------------

The seleniumrunner script will look for all the classes that inherit from
unittest.TestCase on a specified package or module located under this kind of
path::

        namespace.product/namespace/product/tests/seleniumtests

Tests development guidelines
++++++++++++++++++++++++++++

To create a test, there are certain basic rules to follow:

#) The test should inherit from unittest.TestCase class (this can be done
   indirectly also).
#) The test should use certain global variables for the code to work
   on different environments and Plone instances. These are:

        - browser: For the browser used for the tests

        - port: For the port used to communicate with the server

        - url: For the url of the application under test

        - instance: The Plone site name (this depends on
          the name used for the site's creation).

This variables should never be changed inside the test code, as the
seleniumrunner script will set them at runtime according with the parameters
received.

All this rules can be seen applied to the following `Example test`_.

Example test
++++++++++++

The following is an example test, it can be used as the basic
structure for future tests::

        from selenium import selenium
        import unittest

        class NewTest(unittest.TestCase):
            def setUp(self):
                self.verificationErrors = []
                self.selenium = selenium("localhost", port, browser, url)
                self.selenium.start()
            
            def test_new(self):
                sel = self.selenium
				sel.open(instance + "/login.html")
                # Do specific tests in here

            def tearDown(self):
                self.selenium.stop()
                self.assertEqual([], self.verificationErrors)

Notice that the test doesn't have much changes from the basic test exported using
`Selenium IDE <http://seleniumhq.org/projects/ide/>`_, the firefox extension. The 
only difference are the variables used for the instanciation inside the *setUp* method.

.. Note::

    Please notice that the "instance" variable will have to be used in
    each *open* command for the users to provide the correct location
    of the eduCommons plone site to test.

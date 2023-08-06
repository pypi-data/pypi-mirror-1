About
=====

niteoweb.windmill extends Plone's FunctionalTestCase to provide support for
running Windmill tests. This is achieved by adding an additional test layer,
which starts a single-threaded ZServer instance alongside the Windmill server.

Windmill supports most of modern browser. The controller API can be
found at http://trac.getwindmill.com/wiki/ControllerApi.

For more details, see http://getwindmill.com

Remember to read source code, it's very lightweight!

Accessing the Windmill client
=============================

Windmill tests should derive from ``WindmillTestCase``. This provides an
instance of ``WindmillClient`` as ``self.wm``. In addition to supporting the
standard ``WindMillClient`` API, this client has an extra method
``open_site()``, which automatically prepends the Plone site URL when opening
a URL. It is otherwise identical to the ``open()`` method.

FAQ
===

1. How do I synchronize data manipulated by actions in browser and unittests::
	
	In Windmill TestCase, self.site_open() always calls `transaction.commit()` which writes data to ZODB.
	In unittests, just do `import transaction;transaction.commit()` and data will be seen in browser.

Installation
============

easy_install niteoweb.windmill

or add it to eggs directive in buildout;)

Usage
=====

Basic usage::

    from Products.PloneTestCase import PloneTestCase as ptc
    from niteoweb.windmill import WindmillTestCase


    ptc.setupPloneSite()

    class TestSample(WindmillTestCase):
        def afterSetUp(self):
            self.setRoles(['Manager'])
            self.login_user()

        def test_foo(self):
            self.wm.open_site(url="/about")
            self.wm.waits.forPageLoad(timeout=30000)


    def test_suite():
        from unittest import TestSuite, makeSuite
        suite = TestSuite()
        suite.addTest(makeSuite(TestSample))
        return suite

Advanced usage::

  from Products.PloneTestCase import PloneTestCase as ptc

  from niteoweb.windmill import WindmillTestCase, WindmillLayer

  WindmillLayer.site = 'plone2'
  WindmillLayer.windmill_settings['START_FIREFOX'] = False
  WindmillLayer.windmill_settings['START_CHROME'] = True

  ptc.setupPloneSite()

  class TestWM(WindmillTestCase):
      layer = WindmillLayer

      def afterSetUp(self):
          self.setRoles(['Manager'])
          self.login_user()

      def test_foo(self):
          self.wm.open_site('/login_form', site='plone2')
          self.wm.waits.forPageLoad(timeout=30000)

      def test_suite():
          from unittest import TestSuite, makeSuite
          suite = TestSuite()
          suite.addTest(makeSuite(TestWM))
          return suite

and run tests with debug mode to stop on error/failure::

    bin/instance test -s package.module -t test_foo -D 

Known issues
============

* On teardown, you sometimes will get `AttributeError: 'NoneType' object has
  no attribute 'exc_info'`. Ignore it

* Windmill is very poorly tested on Python2.4, submit bugs if you stumble upon
  any;)

TODO
====

* Some simple integration to load existing ZODB storages

CHANGELOG
=========

0.2 (23.11.2009)
****************

- added self.add_user function to testcase (be able to add users with custom
  roles) [Domen Kozar]
- fixed first request failing (due to windmill/plone racecodintions) [Martin Aspeli]
- fixed windmill dependency pulling [Martin Aspeli]

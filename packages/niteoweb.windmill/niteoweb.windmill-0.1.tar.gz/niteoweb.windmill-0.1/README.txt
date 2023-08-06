About
=====

niteoweb.windmill wraps Plone's FunctionalTestCase with support of running Windmill
tests. This is achieved by specifying additional layer which starts ZServer and
Windmill server.

Windmill supports most of modern browser. Controller API can be
found at http://trac.getwindmill.com/wiki/ControllerApi


Terminology
===========

`WindmillTestCase` will have `wm` object available (instance of WindmillClient) as an attribute. This client has an extra `wm.open_site` method which automatically adds plone site to url and later calls `wm.open`.

All configuration is done on `WindmillTestCase.layer` object.


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

* First request made with windmill on startup always fails. This defaults to `http://ip:port/`. Also if you make this default to plone site, some wierd PortletManager error occurs

* On teardown, sometimes you will get `AttributeError: 'NoneType' object has no attribute 'exc_info'`, ignore it

* windmill is very poorly tested on Python2.4, submit bugs if you stumble upon any;)


TODO
====

* Some simple integration to load existing ZODB storages

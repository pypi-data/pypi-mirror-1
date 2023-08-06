import os
import sys
import logging
import posixpath as url_path

import Lifetime
from Testing.ZopeTestCase import utils
from Products.PloneTestCase.PloneTestCase import FunctionalTestCase, default_user, default_password
from Products.PloneTestCase.layer import PloneSite as PloneLayer

import windmill
from windmill.bin.admin_lib import configure_global_settings, setup, teardown
from windmill.authoring.unit import WindmillUnitTestCase
from windmill.authoring import WindmillTestClient


log = logging.getLogger(__name__)

class WindmillLayer:
    site = 'plone'
    windmill_settings = {
        'START_FIREFOX': True,
    }
    test_url = "http://%(host)s:%(port)s/"

    @classmethod
    def setUp(cls):
        # Start the Zope server with one thread
        host, port = utils.startZServer(1)
        site = cls.site
        cls.test_url = cls.test_url % locals()
        log.debug('Starting ZServer on: %s' % cls.test_url)

        # windmill
        windmill.stdout, windmill.stdin = sys.stdout, sys.stdin
        configure_global_settings()
        windmill.settings['TEST_URL'] = cls.test_url
        windmill.settings.update(getattr(cls, "windmill_settings", {}))
        cls.windmill_shell_objects = setup()
        log.debug('Starting Windmill with settings: %r' % windmill.settings)

        # configure client
        cls.wm = WindmillTestClient(__name__)
        def open_site(*a, **kw):
            """little hack to always open an url with name of plone site"""
            if 'url' in kw:
                kw['url'] = url_path.join('/' + (kw.get('site', None) or cls.site), kw['url'].lstrip('/'))
            return cls.wm.open(*a, **kw)
        cls.wm.open_site = open_site

    @classmethod
    def tearDown(cls):
        teardown(cls.windmill_shell_objects)
        Lifetime.shutdown(0, fast=1)


class WindmillPloneLayer(PloneLayer, WindmillLayer):
    pass


class WindmillTestCase(FunctionalTestCase):
    layer = WindmillPloneLayer

    @property
    def wm(self):
        return self.layer.wm

    def login_user(self, username=default_user, password=default_password):
        self.wm.open_site(url="/login_form")
        self.wm.waits.forPageLoad(timeout=30000)
        self.wm.type(id="__ac_name", text=username)
        self.wm.type(id="__ac_password", text=password)
        self.wm.click(name="submit")
        self.wm.waits.forPageLoad(timeout=30000)
        self.wm.asserts.assertNode(xpath="//dl[@class='portalMessage info']/dd")

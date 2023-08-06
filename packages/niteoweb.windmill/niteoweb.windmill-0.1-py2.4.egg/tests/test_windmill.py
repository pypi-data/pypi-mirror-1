from niteoweb.windmill import WindmillTestCase


class TestWM(WindmillTestCase):
    def afterSetUp(self):
        self.setRoles(['Manager'])
        self.login_user()

    def test_foo(self):
        print 'ok'


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestWM))
    return suite

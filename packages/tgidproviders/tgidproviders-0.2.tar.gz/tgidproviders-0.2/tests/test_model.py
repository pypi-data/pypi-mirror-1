from turbogears import testutil, config, database, startup
import cherrypy
from turbogears.identity.soprovider import TG_User, TG_Group, TG_Permission
import unittest

from controllers import IdentityRoot


hub = database.PackageHub("turbogears.identity")

class TestTGUser(testutil.DBTest):
    model = TG_User

    def setUp(self):
        self._identity_on = config.get('identity.on', False)
        config.update({'identity.on': False, 'visit.on': True})

        try:
            self._provider = cherrypy.request.identityProvider
        except AttributeError:
            self._provider= None
        cherrypy.root = IdentityRoot()
        testutil.create_request('/')
        cherrypy.request.identityProvider = None

        startup.startTurboGears()
        testutil.DBTest.setUp(self)

    def tearDown(self):
        testutil.DBTest.tearDown(self)
        startup.stopTurboGears()
        cherrypy.request.identityProvider = self._provider
        config.update({'identity.on': self._identity_on})

    def test_user_exists(self):
        "Test that the samIAm User was created during setup process"
        u = TG_User.by_user_name('samIam')
        assert u.email_address == 'samiam@example.com'

    def test_create_user(self):
        "Test that User can be created outside of a running identity provider."
        u = TG_User(user_name='testcase', email_address='testcase@example.com',
                        display_name='Test Me', password='test')
        assert u.password=='test', u.password


if __name__ == '__main__':

    from utils import setup_identity_tables
    setup_identity_tables()

    suite = unittest.TestSuite()

    for test in [
        TestTGUser,
        ]:
        suite.addTest(unittest.makeSuite(test))

    unittest.TextTestRunner(verbosity=2).run(suite)

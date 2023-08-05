# coding=UTF-8
import re
import unittest
import turbogears
from turbogears import testutil, database, identity, config, startup, expose
from turbogears.identity.soprovider import TG_User, TG_Group, TG_Permission
from controllers import IdentityRoot
from utils import setup_identity_tables, cp, copy_config

#hub = database.AutoConnectHub("sqlite:///:memory:")
hub = database.PackageHub("turbogears.identity")

def mycustomencrypt(password):
    return password+'_custom'

def fmt_request(resource="/", user="samIam", password="secret",
         append_login=True, append_resource = True):
    rr = ""
    if append_resource:
        rr = resource
    rr += "?user_name=%s&password=%s" % (user, password)
    if append_login:
        #TODO: Why is the login parameter needed here?
        rr += "&login=Login"
    return rr
    
class TestBase(unittest.TestCase):
    _original_config = copy_config(config)

    def setUp(self):
        cp.root = IdentityRoot()
        startup.startTurboGears()

    def tearDown(self):
        startup.stopTurboGears()
        config.update(self._original_config)
    
class TestPasswordHashing(TestBase):
    unicode_pwd = u'garçon'
    credentials = fmt_request(append_resource = False)

    def _update_password_encryption(self, method, custom=None):
        "Update config to use a specified password encryption & restart"
        config.update({'identity.soprovider.encryption_algorithm':method})
        if custom:
            config.update({'identity.custom_encryption':custom})
        # for new config values to load
        startup.startTurboGears()
        testutil.create_request('/')

    def _set_and_check_password(self, user_name, password, should_be,
            set_password_raw = False):
        "Set a user's password, and check that it was encrypted correctly"
        hub.begin()
        u = TG_User.by_user_name(user_name)
        if not set_password_raw:
            u.password = password
        else: 
            u.set_password_raw(password)
        u.sync()
        self.failUnlessEqual(u.password, should_be)
        hub.rollback()
        hub.end()
    
    def test_user_password(self):
        "Test if we can set a user password (no encryption algorithm)."
        self._update_password_encryption(None)
        self._set_and_check_password('samIam', 'password', 'password')

    def test_user_password_unicode(self):
        "Test if we can set a user password that is encoded as unicode."
        self._update_password_encryption(None)
        self._set_and_check_password('samIam', self.unicode_pwd,     
                self.unicode_pwd)

    def test_user_password_raw(self):
        "Test that we can store passwords raw (without hashing)."
        self._update_password_encryption('sha1')
        self._set_and_check_password('samIam', 'password', 'password',
                set_password_raw = True)

    def test_user_password_raw_unicode(self):
        self._update_password_encryption('sha1')
        self.unicode_pwd = u'garçon'
        self._set_and_check_password('samIam', self.unicode_pwd, 
               self.unicode_pwd, set_password_raw = True)

    def test_user_password_hashed_sha(self):
        "Test sha hashed password storage."
        self._update_password_encryption('sha1')
        encrypted = '5baa61e4c9b93f3f0682250b6cf8331b7ee68fd8'
        self._set_and_check_password('samIam', 'password', encrypted) 

    def test_user_password_hashed_sha_unicode(self):
        "Test sha hashed unicode password storage"
        self._update_password_encryption('sha1')
        encrypted = '442edb21c491a6e6f502eb79e98614f3c7edf43e'
        self._set_and_check_password('samIam', self.unicode_pwd, encrypted)

    def test_user_password_hashed_md5(self):
        "Test md5 hashed password storage."
        self._update_password_encryption('md5')
        encrypted = '5f4dcc3b5aa765d61d8327deb882cf99'
        self._set_and_check_password('samIam', 'password', encrypted)

    def test_user_password_hashed_md5_unicode(self):
        "Test md5 hashed unicode password storage."
        self._update_password_encryption('md5')
        encrypted = 'c295c4bb2672ca8c432effc53b40bb1e' 
        self._set_and_check_password('samIam', self.unicode_pwd, encrypted)

    def test_user_password_hashed_md5_utf8string(self):
        """Test if a md5 hashed password with unicode characters is stored in
        the database if the password is entered as str (encoded in UTF-8). This
        test ensures that the encryption algorithm does handle non-unicode
        parameters gracefully."""
        self._update_password_encryption('md5')
        encrypted = 'c295c4bb2672ca8c432effc53b40bb1e'
        self._set_and_check_password('samIam',self.unicode_pwd, encrypted)

    def test_user_password_hashed_custom(self):
        "Test if a custom hashed password is stored in the database."
        self._update_password_encryption('custom', 
                  'identity.tests.test_identity.mycustomencrypt')
        self._set_and_check_password('samIam', 'password', 'password_custom')

class TestExternalPasswords(TestBase):
    "Test the external password mechanism support"
    
    def _update_external_password_method(self, method):
        "Update config to use a specified password encryption & restart"
        config.update({'identity.provider':'tgidproviders','identity.method':method})
        # for new config values to load
        startup.startTurboGears()
        testutil.create_request('/')
       
    from tgidproviders import providers 
    def _check_password(self, user, password):
        valid = identity.current_provider.validate_password(user, user, password)
        return valid
    
    #TODO: Fix this test.  It's harmless, but I'd like to be able to show the right
    #TODO:   provider was loaded before we start using it in the tests below.
    #def test_current_provider(self):
    #    'Test that setting identity provider works.'
    #    self._update_external_password_method('blah')
    #    current = turbogears.identity.current_provider
    #    self.failUnless(current.__class__ == 'TGIDProviders', current)

    def test_ldap(self):
        'Test connecting with LDAP.'
        self._update_external_password_method('ldap')
        assert self._check_password('samIam', 'password')
 
    def test_unix_passwd(self):
        'Test password validation with UNIX passwords / NIS db.'
        self._update_external_password_method('unix_passwd')
        assert self._check_password('samIam', 'password')

    def test_smb(self):
        'Test connecting with SMB.'
        self._update_external_password_method('smb')
        assert self._check_password('samIam', 'password')

    def test_database(self):
        'Test connecting with password from user table.'
        self._update_external_password_method('database')
        assert self._check_password('samIam', 'password')

    def test_multiple(self):
        'Test cascading of password methods'
        self._update_external_password_method(['ldap', 'database'])
        assert self._check_password('samIam', 'password')



class TestSecureController(TestBase):
    "Test various features of secure controllers."

    def _assert_firstline(self, expected):
        firstline = cp.response.body[0]
        self.failUnless(expected in firstline, expected +" not in " +firstline)

    def test_user_password_parameters(self):
        "Controller can receive user_name and password parameters."
        testutil.create_request(fmt_request("/new_user_setup", append_login=0))
        self._assert_firstline('samIam secret')

    def test_bad_login(self):
        "Test that we are denied access if we provide a bad login."
        req = fmt_request("/logged_in_only", password = 'badpasswd',
                    append_login = False)
        testutil.create_request(req)
        self._assert_firstline('identity_failed_answer')

    def test_anonymous_browsing(self):
        "Test if we can show up anonymously."
        testutil.create_request('/')
        assert identity.current.anonymous

    def test_deny_anonymous(self):
        "Test that we have secured an url from anonymous users."
        testutil.create_request('/logged_in_only')
        self._assert_firstline('identity_failed_answer')

    def test_deny_anonymous_viewable(self):
        "Test that a logged in user can see a not_anonymous resources."
        testutil.create_request(fmt_request('/logged_in_only'))
        self._assert_firstline('logged_in_only')

    def test_require_group(self):
        "Test that a anonymous user can't access resources secured to a group"
        testutil.create_request('/in_peon_group')
        self._assert_firstline('identity_failed_answer')

    def test_require_expose_required_permission(self):
        "Test that the require decorator sets needed attributes on the method."
        testutil.create_request('/test_exposed_require')
        self._assert_firstline('require is exposed')

    def test_require_group_viewable(self):
        "Test that a user that's in the proper group has correct access."
        testutil.create_request(fmt_request('/in_peon_group'))
        self._assert_firstline('in_peon_group')

    def test_user_not_in_right_group(self):
        "Test that a user is denied access if they aren't in the right group."
        testutil.create_request(fmt_request('/in_admin_group'))
        self._assert_firstline('identity_failed_answer')

    def test_require_permission(self):
        "Test that an anonymous user is denied access to a restricted url."
        testutil.create_request('/has_chopper_permission')
        self._assert_firstline('identity_failed_answer')

    def test_require_permission_viewable(self):
        "Test that a user with proper permissions can see a restricted url."
        testutil.create_request(fmt_request('/has_chopper_permission'))
        self._assert_firstline('has_chopper_permission')

    def test_user_lacks_permission(self):
        "Test permission failure."
        testutil.create_request(fmt_request('/has_boss_permission'))
        self._assert_firstline('identity_failed_answer')

    def test_user_info_available(self):
        "Test that we can see user information inside our controller."
        testutil.create_request(fmt_request("/user_email"))
        self._assert_firstline('samiam@example.com')

    def test_restricted_subdirectory(self):
        "Test that we can restrict access to a whole subdirectory."
        testutil.create_request('/peon_area/index')
        self._assert_firstline('identity_failed_answer')

    def test_restricted_subdirectory_viewable(self):
        "Test sucessful access to restricted resource."
        testutil.create_request(fmt_request("/peon_area/index"))
        self._assert_firstline('restricted_index')

    def test_decoratator_in_restricted_subdirectory(self):
        "Test that child resource can require different permission it's parent."
        testutil.create_request(fmt_request('/peon_area/in_other_group'))
        self._assert_firstline('in_other_group')

    def test_decoratator_failure_in_restricted_subdirectory(self):
        "Test access failure from a restricted child resource."
        testutil.create_request(fmt_request('/peon_area/in_admin_group'))
        self._assert_firstline('identity_failed_answer')

    def test_explicit_checks_in_restricted_subdirectory(self):
        "Test explicit permission checks inside a controller method."
        request = fmt_request("/peon_area/in_other_group_explicit_check")
        testutil.create_request(request)
        self._assert_firstline('in_other_group')

    def test_throwing_identity_exception_in_restricted_subdirectory(self):
        "Test explicit throw of IdentityException inside a controller method."
        request = fmt_request("/peon_area/in_admin_group_explicit_check")
        testutil.create_request(request)
        self._assert_firstline('identity_failed')

    def test_logout(self):
        "Test that logout works and the session is not valid afterward."
        testutil.create_request(fmt_request('/in_peon_group'))
        self.assertEquals("samIam", cp.identity.user_name)

        x = re.match("Set-Cookie: (.*?); Path.*", str(cp.response.simple_cookie))
        session_id = x.group(1)
        testutil.create_request('/logout', headers={'Cookie': session_id })

        self.assertEquals(None, cp.identity.user_name)
        assert cp.request.identity.anonymous

    def test_logout_with_set_identity(self):
        "Test that logout works when set_identity_user is used. (no visit_key)"
        request = testutil.DummyRequest()
        old_user = testutil.test_user
        user = TG_User.by_user_name("samIam")
        testutil.set_identity_user(user)
        testutil.attach_identity(request)
        testutil.set_identity_user(old_user)
        testutil.call_with_request(cp.root.logout, request)
        identity = request.identity
        assert identity.anonymous

if __name__ == '__main__':
   
    setup_identity_tables()
    suite = unittest.TestSuite()

    for test in [TestPasswordHashing, TestSecureController, TestExternalPasswords]:
        suite.addTest(unittest.makeSuite(test))

    unittest.TextTestRunner(verbosity=2).run(suite)

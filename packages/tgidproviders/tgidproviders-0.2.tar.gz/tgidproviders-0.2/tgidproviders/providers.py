""" TurboGears Identity providers to check passwords against 
alternative sources, such as an LDAP directory, SMB domain, or
UNIX password system.

Only authentication is overriden from the TurboGears default, 
authorization is left alone. In other words, passwords are checked, but
groups & permissions are still left to the database, and not retrieved
from the external source.  Stated still differently, the only 
difference between this provider and the standard one is that this 
provider ignores the password field in the user model.


Be sure to add the following lines under the [global] section in a config file (such as app.cfg) for your projects:

identity.provider='tgidproviders'
identity.method=['database', 'ldap']

identity.method can be one of: 'database', which will use the default TG password validation system (eg, the password field on the User table), 'ldap', which will validate against an LDAP directory, 'smb' validates against Windows domains, 'unix_passwd' validates against a UNIX password / NIS system.

Some methods require additional configuration.  For example, the SMB
method requires that the smb_domain be set:
identity.smb.domain="PUT_YOUR_DOMAIN_HERE"

The LDAP provider uses the following configuration variables (shown with their default values):
identity.ldap.host="localhost"
identity.ldap.port=389
identity.ldap.basedn="dc=localhost"
identity.ldap.filter="(sAMAccountName=s)"

If you're using OpenLDAP, you might try a filter like so:
identity.ldap.filter="(&(objectClass=inetOrgPerson)(uid=s))"
"""

from turbogears import config
from turbogears.identity import soprovider, saprovider
import logging 
import logging.config

#logging.config.fileConfig("logging.cfg")
logging.basicConfig()
log = logging.getLogger('identity')
log.setLevel(logging.INFO)

available_methods = ['database']
try:
    from win32security import (LogonUser, LOGON32_LOGON_NETWORK,
                               LOGON32_PROVIDER_DEFAULT, error as LogonError)
    available_methods.append('smb')
except ImportError:
    logging.warn('Win32 imports failed.  SMB authentication not available.')

try:
    import ldap
    available_methods.append('ldap')
except ImportError:
    logging.warn('LDAP import failed.  LDAP authentication not available.')

try: 
    from crypt import crypt
    import pwd
    import spwd
    available_methods.append('unix_passwd')
except ImportError:
    logging.warn('Crypt libraries not installed. UNIX passwd authentication not available.')

    
get_cfg = config.get

if get_cfg('sqlobject.dburi', None):
    BaseProvider = soprovider.SqlObjectIdentityProvider
    log.info('Identity base: soprovider')
elif get_cfg('sqlalchemy.dburi', None):
    BaseProvider = saprovider.SqlAlchemyIdentityProvider
    log.info('Identity base: saprovider')

class TGIDProviders(BaseProvider):
    '''IdentityProvider that validates passwords from external sources.
    Supported sources are LDAP, SMB, and UNIX passwd files.
    '''

    def __init__(self):
        ''' 
        Establish configuration settings from environment.
        If no methods are listed in the config, default to just
        using the default provider's database lookup.
        '''
        super(TGIDProviders, self).__init__()

        methods = get_cfg('identity.method')
        if not methods: 
            methods = get_cfg('identity.methods')
            if not methods:
                methods = ['database']
                log.warn("Identity method not set in config --"
                         "Using default of %s." % methods)

        # Make sure we have an iterable and not just a string
        if not hasattr(methods, '__iter__'):
            methods = [methods]
        log.info('identity.method :: %s' % methods)
        self.methods = methods
         
        # Get SMB config, if applicable
        self.smb_domain = get_cfg("identity.smb.domain", None)
        if self.smb_domain:
            log.info("smb.domain :: %s" % self.smb_domain)
   
        # Get LDAP config, if applicable
        self.ldap_host = get_cfg("identity.ldap.host", "localhost")
        self.ldap_port = get_cfg("identity.ldap.port", 389)
        self.ldap_basedn = get_cfg("identity.ldap.basedn", "dc=localhost")
        self.ldap_filter = get_cfg("identity.ldap.filter", r"(sAMAccountName=%s)")

        if self.ldap_host: 
            log.info("ldap host :: %s" % self.ldap_host)
            log.info("ldap port :: %d" % self.ldap_port)
            log.info("ldap basedn :: %s" % self.ldap_basedn)

        #self.autocreate = get("identity.autocreate", False)
        #log.info("autocreate :: %s" % self.autocreate)

    def validate_password_smb(self, user, user_name, password):
        '''
        Validates user_name and password against a Windows/Samba domain
        specified in the identity.smb_domain config parameter.
        It's just a wrapper for win32security.LogonUser().
        '''
        from win32security import (LogonUser, LOGON32_LOGON_NETWORK, 
                         LOGON32_PROVIDER_DEFAULT, error as LogonError)

        try:
            token = LogonUser(user_name, self.smb_domain, password, 
                      LOGON32_LOGON_NETWORK,  LOGON32_PROVIDER_DEFAULT)
        except LogonError, e:
            result = False
        else:
            result = bool(token)   # usually True
        if not result:
            log.info('SMB password validation failed for user: %s' % user_name)
        return result

    def validate_password_unix_passwd(self, user, user_name, password):
        """Validates user_name and password against UNIX password
        files / NIS database.
        """
        log.debug("Validating User '%s' against PWD database" % user_name)

        try:
            # Get the DES encrypted password from the password database
            try:
               xx = spwd.getspnam(user_name)
            except KeyError:
               xx = pwd.getpwnam(user_name)
            crypted_password = xx[1]
            # Get the salt from the crypted password.
            #salt = crypted_password[:2]
            salt = crypted_password[:crypted_password.find('$',3)+1]
            if salt in ['x', '*']:
                log.warning(
                    'Skipping UNIX password check because getpwnam did '
                    'not return the encrypted password.'
                    'Please read the documentation.')
                return False
        except KeyError, e:
            log.error("User '%s' not found in UNIX PWD database" % user_name)
            return False

        auth_password = crypt(password, salt)

        # Make sure the encrypted passwords match
        match = crypted_password == auth_password

        if not result:
            log.info('UNIX password validation failed for user: %s' % user_name)
        return match


    def validate_password_ldap(self, user, user_name, password):
        '''
        Validates user_name and password against an LDAP directory.
        The default filter is set for an AD domain (see init).
        '''

        ldapcon = ldap.open(self.ldap_host, self.ldap_port)
        try:
            filter = self.ldap_filter % user_name
        except TypeError:
            raise Exception(
              "LDAP filter string must have placeholder for user name")

        rc = ldapcon.search(self.ldap_basedn, ldap.SCOPE_SUBTREE, filter)

        objects = ldapcon.result(rc)[1]

        if(len(objects) == 0):
            log.warning("No such LDAP user: %s" % user_name)
            return False
        elif(len(objects) > 1):
            log.error("Too many LDAP users: %s" % user_name)
            return False

        dn = objects[0][0]

        try:
            rc = ldapcon.simple_bind(dn, password)
            ldapcon.result(rc)
        except ldap.INVALID_CREDENTIALS:
            log.error("Invalid LDAP password supplied for %s" % user_name)
            return False

        return True

    def validate_password(self, user, user_name, password):
        '''Validate password using the method(s) supplied in config.'''

        known_methods = {
            'database': super(TGIDProviders, self).validate_password,
            'ldap': self.validate_password_ldap,
            'smb': self.validate_password_smb,
            'unix_passwd': self.validate_password_unix_passwd
        }
        args = [user, user_name, password]

        ok = False 
        for method in self.methods:
            if not method in available_methods:
                # Just log a message here instead of raising an error, because it's useful
                #   to be able to test on a machine that doesn't have all of the methods installed
                #   that you're planning on using in production.
                log.debug("Password validation method %s skipped. Not available.")
                continue
            ok = known_methods[method](*args)
            log.debug("Password validation method %s, user %s ok? :: %s"
                     % (method, user_name, ok))
            if ok:
                return True
        return ok


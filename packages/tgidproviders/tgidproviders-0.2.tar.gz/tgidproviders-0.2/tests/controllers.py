# coding=UTF-8
import turbogears
from turbogears import testutil, database, identity, config, startup, expose

#hub = database.AutoConnectHub("sqlite:///:memory:")
hub = database.PackageHub("turbogears.identity")

class RestrictedArea(turbogears.controllers.Controller, identity.SecureResource):

    require = identity.in_group('peon')

    @expose()
    def index(self):
        return "restricted_index"

    @expose()
    @identity.require(identity.in_group('admin'))
    def in_admin_group(self):
        return 'in_admin_group'

    @expose()
    @identity.require(identity.in_group('other'))
    def in_other_group(self):
        return 'in_other_group'

    @expose()
    def in_admin_group_explicit_check(self):
        if 'admin' not in identity.current.groups:
            raise identity.IdentityFailure("You need to be an Admin")
        else:
            return 'in_admin_group'

    @expose()
    def in_other_group_explicit_check(self):
        if 'other' not in identity.current.groups:
            raise identity.IdentityException
        else:
            return 'in_other_group'

class IdentityRoot(turbogears.controllers.RootController):

    peon_area = RestrictedArea()

    @expose()
    def index(self):
        pass

    @expose()
    def identity_failed(self):
        return 'identity_failed_answer'

    @expose()
    @identity.require(identity.not_anonymous())
    def logged_in_only(self):
        return 'logged_in_only'

    @expose()
    @identity.require(identity.in_group('peon'))
    def in_peon_group(self):
        return 'in_peon_group'

    @expose()
    def test_exposed_require(self):
        if not hasattr(self.in_peon_group, '_require'):
            return 'no _require attr'
        if not isinstance(self.in_peon_group._require, identity.in_group):
            return 'not correct class'
        if 'peon' != self.in_peon_group._require.group_name:
            return 'not correct group name'
        return '_require is exposed'

    @expose()
    @identity.require(identity.in_group('admin'))
    def in_admin_group(self):
        return 'in_admin_group'

    @expose()
    @identity.require(identity.has_permission('chops_wood'))
    def has_chopper_permission(self):
        return 'has_chopper_permission'

    @expose()
    @identity.require(identity.has_permission('boss_permission'))
    def has_boss_permission(self):
        return "has_boss_permission"

    @expose()
    def logout(self):
        identity.current.logout()
        return "logged out"

    @expose()
    @identity.require(identity.not_anonymous())
    def user_email(self):
        return identity.current.user.email_address

    @expose()
    def new_user_setup(self, user_name, password): #s=*args):
        return '%s %s' % (user_name, password)

def run_once():
    "Set up tables for identity tests."
    identity.current_provider.create_provider_model()
    #if TG_User.select().count() != 0:  return
   
    user = TG_User(user_name='samIam', email_address='samiam@example.com',
                   display_name='Samuel Amicus', password='secret')
    peon_group = TG_Group(group_name="peon", display_name="Regular Peon")
    admin_group = TG_Group(group_name="admin", display_name="Administrator")
    other_group = TG_Group(group_name="other", display_name="Another Group")
    chopper_perm = TG_Permission(permission_name='chops_wood',
                                 description="Wood Chopper")
    boss_perm = TG_Permission(permission_name='bosses_people',
                              description="Benevolent Dictator")
    peon_group.addTG_Permission(chopper_perm)
    admin_group.addTG_Permission(boss_perm)
    user.addTG_Group(peon_group)
    user.addTG_Group(other_group)

if __name__ == '__main__':
    from utils import setup_identity_tables
    setup_identity_tables()

    turbogears.start_server(IdentityRoot())


from turbogears.identity.soprovider import TG_User, TG_Group, TG_Permission
from turbogears import identity

def setup_identity_tables():
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

class WrapCherryPy(object):
    """Wrap CherryPy so that only it's most basic features are available.
    The hope is that by restricting ourselves to just this skeleton,
    we should be able to support other servers more easily in the future.
    (By creating equivalent wrappers & switching between them.)
    """
    import cherrypy
    
    # These four properties are the entirety of our interface.
    def get_request(self):
        return self.cherrypy.serving.request
    request = property(get_request)
    
    def get_response(self):
        return self.cherrypy.response
    response = property(get_response)
    
    def get_identity(self):
        return self.cherrypy.request.identity
    identity = property(get_identity)
    
    def get_root(self):
        return self.cherrypy.root
    def set_root(self, root):
        self.cherrypy.root = root
        return root    
    root = property(get_root, set_root)
cp = WrapCherryPy()

def copy_config(config):
    "Copy a turbogears config"
    return config.config.configs.copy()


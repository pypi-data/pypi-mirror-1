
class Config(object):
    def __init__(self):
        from pylons import config as pylons_config
        self.index_template        = 'genshi:tg.ext.silverplate.templates.index'
        self.profile_template      = 'genshi:tg.ext.silverplate.templates.profile'
        self.group_edit_template   = 'genshi:tg.ext.silverplate.templates.group'
        self.groups_template       = 'genshi:tg.ext.silverplate.templates.groups'
        self.group_template        = 'genshi:tg.ext.silverplate.templates.profile'
        self.permissions_template  = 'genshi:tg.ext.silverplate.templates.permissions'
        self.permission_template   = 'genshi:tg.ext.silverplate.templates.profile'
        self.users_template        = 'genshi:tg.ext.silverplate.templates.users'
        self.user_template         = 'genshi:tg.ext.silverplate.templates.profile'
        self.registration_template = 'genshi:tg.ext.silverplate.templates.registration'
        
        self.UserClass = pylons_config['sa_auth']['user_class']
        self.GroupClass = pylons_config['sa_auth']['group_class']
        self.PermissionClass = pylons_config['sa_auth']['permission_class']
        self.users_table = pylons_config['sa_auth']['users_table']
        self.groups_table = pylons_config['sa_auth']['groups_table']
        self.permissions_table = pylons_config['sa_auth']['permissions_table']
        self.password_encryption_method = pylons_config['sa_auth']['password_encryption_method']

config = Config()

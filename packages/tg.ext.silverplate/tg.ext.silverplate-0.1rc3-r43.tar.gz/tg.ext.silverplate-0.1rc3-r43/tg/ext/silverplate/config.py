from pylons import config as pylons_config

class Config(object):pass

config = Config()

config.index_template        = 'genshi:tg.ext.silverplate.templates.index'
config.profile_template      = 'genshi:tg.ext.silverplate.templates.profile'
config.group_edit_template   = 'genshi:tg.ext.silverplate.templates.group'
config.groups_template       = 'genshi:tg.ext.silverplate.templates.groups'
config.group_template        = 'genshi:tg.ext.silverplate.templates.profile'
config.permissions_template  = 'genshi:tg.ext.silverplate.templates.permissions'
config.permission_template   = 'genshi:tg.ext.silverplate.templates.profile'
config.users_template        = 'genshi:tg.ext.silverplate.templates.users'
config.user_template         = 'genshi:tg.ext.silverplate.templates.profile'
config.registration_template = 'genshi:tg.ext.silverplate.templates.registration'

config.UserClass = pylons_config['identity']['user_class']
config.GroupClass = pylons_config['identity']['group_class']
config.PermissionClass = pylons_config['identity']['permission_class']
config.users_table = pylons_config['identity']['users_table']
config.groups_table = pylons_config['identity']['groups_table']
config.permissions_table = pylons_config['identity']['permissions_table']
config.password_encryption_method = pylons_config['identity']['password_encryption_method']

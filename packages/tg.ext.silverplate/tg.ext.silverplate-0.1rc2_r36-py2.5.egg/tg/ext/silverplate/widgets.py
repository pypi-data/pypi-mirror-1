"""
controller Module

Classes:
Name                               Description
DBMechanic

Exceptions:
None

Functions:
None

Copyright (c) 2008 Christopher Perkins
Original Version by Christopher Perkins 2008
Released under MIT license.
"""
from cStringIO import StringIO
from genshi import HTML
import pylons.config

#widget imports
from tw.api import Widget, CSSLink
from tw.forms.fields import PasswordField, HiddenField,TextField
from formencode.validators import FieldsMatch
from formencode import Schema
from dbsprockets.primitives import makeForm, makeTable, getTableValue
from dbsprockets.sessionconfig import EditRecordSessionConfig
from tg.ext.silverplate.config import config

UserClass = pylons.config['identity']['user_class']
GroupClass = pylons.config['identity']['group_class']
PermissionClass = pylons.config['identity']['permission_class']
users_table = pylons.config['identity']['users_table']

password_encryption_method = pylons.config['identity']['password_encryption_method']

requiredFields = ['password', 'user_name', 'email_address']
limitFields    = ['user_name', 'display_name', 'email_address', 'password', ]

additionalFields = [PasswordField('passwordVerification', label_text='Verify'),]

formValidator =  Schema(chained_validators=(FieldsMatch('password',
                                                'passwordVerification',
                                                messages={'invalidNoMatch': 
                                                          "Passwords do not match"}),))
registrationForm = makeForm(UserClass, 
                            'register', 
                            requiredFields=requiredFields, 
                            limitFields=limitFields, 
                            additionalFields=additionalFields,
                            fieldAttrs={'display_name':{'style':'height:20px;', 'cols':19, 'rows':2}, 
                                        'email_address':{'style':'height:20px;','cols':19, 'rows':2}},
                            formValidator=formValidator)

userForm = makeForm(UserClass,
                    'edit_user', 
                    requiredFields=requiredFields, 
                    hiddenFields=['user_id',],
                    omittedFields=['password'],
                    disabledFields=['user_name'],
                    #limitFields=limitFields, 
                    #additionalFields=additionalFields, 
                    fieldAttrs={'display_name':{'style':'height:20px;', 'cols':19, 'rows':2}, 
                                'email_address':{'style':'height:20px;','cols':19, 'rows':2}},
                    formValidator=formValidator)

def admin_links(viewConfig, row):
    pks = viewConfig.metadata.primaryKeys()
    pkString = viewConfig._writePKsToURL(pks, row)
    links = StringIO()
    links.write('<a href="user')
    links.write(pkString)
    links.write('">edit</a>|')
    links.write('<a href="delete_user')
    links.write(pkString)
    links.write('">delete</a>')
    return HTML(links.getvalue())

omittedFields    = ['user_id','password']
usersTable = makeTable(UserClass, controller='edit', omittedFields=omittedFields, makeLinks=admin_links)

additionalFields = [PasswordField('passwordVerification', label_text='Verify'), HiddenField('came_from'),]
profileForm = makeForm(UserClass,
                    'edit_profile', 
                    requiredFields=requiredFields, 
                    limitFields=limitFields, 
                    hiddenFields=['user_id', 'came_from'],
                    additionalFields=additionalFields, 
                    disabledFields=['user_name'],
                    fieldAttrs={'display_name':{'style':'height:20px;', 'cols':19, 'rows':2}, 
                                'email_address':{'style':'height:20px;','cols':19, 'rows':2}},
                    formValidator=formValidator)

groupEditForm = makeForm(GroupClass,
                    'edit_group', 
                    hiddenFields=['group_id', 'created'],
                    disabledFields=['created']
                    )

groupAddForm = makeForm(GroupClass,
                    'add_group', 
                    omittedFields=['group_id', config.users_table+'s', config.permissions_table+'s', 'created'],
                    fieldAttrs={'display_name':{'style':'height:20px;', 'cols':19, 'rows':2}},
                    )

permissionEditForm = makeForm(PermissionClass,
                    'edit_permission', 
                    hiddenFields=['permission_id', 'created'],
                    omittedFields=['created'],
                    )
permissionAddForm = makeForm(PermissionClass,
                    'add_permission', 
                    omittedFields=['permission_id', config.groups_table+'s', 'created'],
                    fieldAttrs={'description':{'style':'height:40px;', 'cols':19, 'rows':2}},
                    )

def group_links(viewConfig, row):
    pks = viewConfig.metadata.primaryKeys()
    pkString = viewConfig._writePKsToURL(pks, row)
    links = StringIO()
    links.write('<a href="group')
    links.write(pkString)
    links.write('">edit</a>|')
    links.write('<a href="delete_group')
    links.write(pkString)
    links.write('">delete</a>')
    return HTML(links.getvalue())

omittedFields    = ['group_id']
groupsTable = makeTable(GroupClass, controller='', omittedFields=omittedFields, makeLinks=group_links)

def permission_links(viewConfig, row):
    pks = viewConfig.metadata.primaryKeys()
    pkString = viewConfig._writePKsToURL(pks, row)
    links = StringIO()
    links.write('<a href="permission')
    links.write(pkString)
    links.write('">edit</a>|')
    links.write('<a href="delete_permission')
    links.write(pkString)
    links.write('">delete</a>')
    return HTML(links.getvalue())

omittedFields    = ['permission_id']
permissionsTable = makeTable(PermissionClass, controller='', omittedFields=omittedFields, makeLinks=permission_links)

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
from dbsprockets.primitives import getTableValue, make_form, make_table
from dbsprockets.sessionconfig import EditRecordSessionConfig
from tg.ext.silverplate.config import config

UserClass = pylons.config['sa_auth']['user_class']
GroupClass = pylons.config['sa_auth']['group_class']
PermissionClass = pylons.config['sa_auth']['permission_class']

password_encryption_method = pylons.config['sa_auth']['password_encryption_method']

required_fields = ['password', 'user_name', 'email_address']
limit_fields    = ['user_name', 'display_name', 'email_address', 'password', ]

additional_fields = {'passwordVerification':PasswordField('passwordVerification', label_text='Verify'),}

form_validator =  Schema(chained_validators=(FieldsMatch('password',
                                                'passwordVerification',
                                                messages={'invalidNoMatch':
                                                          "Passwords do not match"}),))
registration_form = make_form(UserClass,
                            'register',
                            required_fields    = required_fields,
                            limit_fields       = limit_fields+['passwordVerification',],
                            additional_fields  = additional_fields,
                            field_attrs        = {'display_name':{'style':'height:20px;', 'cols':19, 'rows':2},
                                                  'email_address':{'style':'height:20px;','cols':19, 'rows':2}},
                            form_validator     = form_validator)

user_form = make_form(UserClass,
                    'edit_user',
                    required_fields=required_fields,
                    hidden_fields=['user_id',],
                    omitted_fields=['password'],
                    disabled_fields=['user_name'],
                    #limit_fields=limit_fields,
                    #additional_fields=additional_fields,
                    field_attrs={'display_name':{'style':'height:20px;', 'cols':19, 'rows':2},
                                'email_address':{'style':'height:20px;','cols':19, 'rows':2}},
                    form_validator=form_validator)

def admin_links(view_config, row):
    pks = view_config.metadata.primary_keys()
    pkString = view_config._writePKsToURL(pks, row)
    links = StringIO()
    links.write('<a href="user')
    links.write(pkString)
    links.write('">edit</a>|')
    links.write('<a href="delete_user')
    links.write(pkString)
    links.write('">delete</a>')
    return HTML(links.getvalue())

omitted_fields    = ['user_id','password']
users_table = make_table(UserClass, controller='edit', omitted_fields=omitted_fields, make_links=admin_links)

additional_fields = {'passwordVerification':PasswordField('passwordVerification', label_text='Verify'),
                    'came_from':HiddenField('came_from')}

profile_form = make_form(UserClass,
                    'edit_profile',
                    required_fields=required_fields,
                    limit_fields=limit_fields,
                    hidden_fields=['user_id', 'came_from'],
                    additional_fields=additional_fields,
                    disabled_fields=['user_name'],
                    field_attrs={'display_name':{'style':'height:20px;', 'cols':19, 'rows':2},
                                'email_address':{'style':'height:20px;','cols':19, 'rows':2}},
                    form_validator=form_validator)

group_edit_form = make_form(GroupClass,
                    'edit_group',
                    hidden_fields=['group_id', 'created'],
                    disabled_fields=['created']
                    )

group_add_form = make_form(GroupClass,
                    'add_group',
                    omitted_fields=['group_id', config.users_table+'s', config.permissions_table+'s', 'created'],
                    field_attrs={'display_name':{'style':'height:20px;', 'cols':19, 'rows':2}},
                    )

permission_edit_form = make_form(PermissionClass,
                    'edit_permission',
                    hidden_fields=['permission_id', 'created'],
                    omitted_fields=['created'],
                    )
permission_add_form = make_form(PermissionClass,
                    'add_permission',
                    omitted_fields=['permission_id', config.groups_table+'s', 'created'],
                    field_attrs={'description':{'style':'height:40px;', 'cols':19, 'rows':2}},
                    )

def group_links(view_config, row):
    pks = view_config.metadata.primary_keys()
    pkString = view_config._writePKsToURL(pks, row)
    links = StringIO()
    links.write('<a href="group')
    links.write(pkString)
    links.write('">edit</a>|')
    links.write('<a href="delete_group')
    links.write(pkString)
    links.write('">delete</a>')
    return HTML(links.getvalue())

omitted_fields    = ['group_id']
groups_table = make_table(GroupClass,
                         controller='',
                         omitted_fields=omitted_fields,
                         make_links=group_links)

def permission_links(view_config, row):
    pks = view_config.metadata.primary_keys()
    pkString = view_config._writePKsToURL(pks, row)
    links = StringIO()
    links.write('<a href="permission')
    links.write(pkString)
    links.write('">edit</a>|')
    links.write('<a href="delete_permission')
    links.write(pkString)
    links.write('">delete</a>')
    return HTML(links.getvalue())

omitted_fields    = ['permission_id']
permissions_table = make_table(PermissionClass,
                              controller='',
                              omitted_fields=omitted_fields,
                              make_links=permission_links)

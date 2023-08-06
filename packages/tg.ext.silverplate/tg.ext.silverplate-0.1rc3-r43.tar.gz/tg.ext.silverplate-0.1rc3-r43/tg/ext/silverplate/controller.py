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
import md5
import sha
from cStringIO import StringIO
from genshi import HTML

import sqlalchemy
import pylons
from pylons import config as pylons_config, request

from tg.decorators import expose, validate
from tg.controllers import redirect
from tg import flash, TGController, url


#widget imports
from tw.api import Widget, CSSLink
from tw.forms.fields import PasswordField, HiddenField,TextField
from formencode.validators import FieldsMatch
from formencode import Schema
from dbsprockets.primitives import makeForm, makeTable, getTableValue
from dbsprockets.sessionconfig import EditRecordSessionConfig
from tg.ext.silverplate.widgets import registrationForm, userForm, usersTable, profileForm, groupsTable, groupEditForm, groupAddForm, permissionsTable, permissionAddForm, permissionEditForm
from tg.ext.silverplate.config import config

__all__ = ['BaseController', 'SilverPlate']


class BaseController(TGController):
    """Basis TurboGears controller class which is derived from
    TGController
    """
    
    def __call__(self, environ, start_response):
        """Invoke the Controller"""
        # TGController.__call__ dispatches to the Controller method
        # the request is routed to. This routing information is
        # available in environ['pylons.routes_dict']

        # Create a container to send widgets to the template. Only those sent
        # in here will have their resources automatically included in the
        # template
        context.w = WidgetBunch()
#        context.w.css = dbsprocketsCss
        try:
            return TGController.__call__(self, environ, start_response)
        finally:
            pass
            #after everything is done clear out the Database Session
            #so to eliminate possible cross request DBSession polution.
            #model.DBSession.remove()

            
def modify_password(password):
    if "sha1" == config.password_encryption_method:
        password = sha.new(password).hexdigest()
    elif "md5" == config.password_encryption_method:
        password = md5.new(password).hexdigest()
    password = unicode(password)
    return password

class SilverPlate(BaseController):
    def __init__(self, provider, *args, **kwargs):
        self.provider = provider
        BaseController.__init__(self, *args, **kwargs)
        self.userSessionConfig = EditRecordSessionConfig(config.users_table+'SessionConfig', provider, config.users_table)
        self.groupSessionConfig = EditRecordSessionConfig(config.groups_table+'SessionConfig', provider, config.groups_table)
        self.permissionSessionConfig = EditRecordSessionConfig(config.permissions_table+'SessionConfig', provider, config.permissions_table)

    @expose(config.index_template)
    def index(self):
        return dict()

    @expose(config.groups_template)
    def groups(self, **kw):
        value = getTableValue(config.GroupClass)
        pylons.c.groups = groupsTable
        pylons.c.form = groupAddForm
        return dict(value=value, formValue=kw)
    
    @expose(config.group_template)
    def group(self, group_id):
        data = self.groupSessionConfig.getValue(dict(group_id=group_id))
        pylons.c.edit = groupEditForm
        return dict(value=data)

    @expose()
    @validate(form=groupEditForm, error_handler=group)
    def edit_group(self, **kw):
        params = pylons.request.params.copy()
        self.create_relationships(config.groups_table, params)
        self.provider.edit(tableName=config.groups_table, values=kw)
        redirect('groups')

    @expose()
    @validate(form=groupAddForm, error_handler=groups)
    def add_group(self, **kw):
        self.provider.add(config.groups_table, values=kw)
        flash('Your Group has been successfully created.')
        redirect('groups')

    @expose()
    def delete_group(self, group_id):
        self.provider.delete(config.groups_table, values=dict(group_id=group_id))
        flash('Your Group has been successfully removed.')
        redirect('groups')

    @expose(config.permissions_template)
    def permissions(self, **kw):
        value = getTableValue(config.PermissionClass)
        pylons.c.permissions = permissionsTable
        pylons.c.form = permissionAddForm
        return dict(value=value, formValue=kw)

    @expose(config.permission_template)
    def permission(self, permission_id):
        data = self.permissionSessionConfig.getValue(dict(permission_id=permission_id))
        pylons.c.edit = permissionEditForm
        return dict(value=data)

    @expose()
    @validate(form=permissionAddForm, error_handler=permissions)
    def add_permission(self, **kw):
        self.provider.add(config.permissions_table, values=kw)
        flash('Your Permission has been successfully created.')
        redirect('permissions')

    @expose()
    @validate(form=permissionEditForm, error_handler=permission)
    def edit_permission(self, **kw):
        params = pylons.request.params.copy()
        self.create_relationships(config.permissions_table, params)
        self.provider.edit(tableName=config.permissions_table, values=kw)
        redirect('permissions')

    @expose()
    def delete_permission(self, permission_id):
        self.provider.delete(config.permissions_table, values=dict(permission_id=permission_id))
        flash('Your Permission has been successfully removed.')
        redirect('permissions')

    @expose(config.users_template)
    def users(self):
        value = getTableValue(config.UserClass)
        pylons.c.users = usersTable
        return dict(value=value)

    @expose(config.user_template)
    def user(self, user_id):
        user_data = self.userSessionConfig.getValue(dict(user_id=user_id))
        pylons.c.edit = userForm
        user_data['passwordVerification'] = user_data['password']
        return dict(value=user_data)

    @expose()
    def edit_user(self, **kw):
        params = pylons.request.params.copy()
        self.create_relationships(config.users_table, params)
        self.provider.edit(tableName=config.users_table, values=kw)
        redirect('users')

    @expose()
    def delete_user(self, user_id):
        self.provider.delete(config.users_table, values=dict(user_id=user_id))
        flash('Your User has been successfully removed.')
        redirect('users')
        
    def create_relationships(self, tableName, params):
        #this might become a decorator
        #check to see if the table is a many-to-many table first
        if tableName in self.provider.getManyToManyTables():
            return
        #right now many-to-many only supports single primary keys
        pk=self.provider.getPrimaryKeys(tableName)
        assert len(pk)==1
        id = params[pk[0]]
        relationships = {}
        for key, value in params.iteritems():
            if key.startswith('many_many_'):
                relationships.setdefault(key[10:], []).append(value)
        for key, value in relationships.iteritems():
            self.provider.setManyToMany(tableName, id, key, value)

#profile stuff below
class SilverPlateProfile(BaseController):
    def __init__(self, provider, *args, **kwargs):
        self.provider = provider
        BaseController.__init__(self, *args, **kwargs)

    def _check_identity(self, user_id, came_from):
        identity = request.environ.get('repoze.who.identity')
        if identity is None:
            flash('you must be logged into your user account to edit your profile.')
            redirect(url('/'))
        user_id = int(user_id)
        if identity['user'].user_id != user_id:
            flash('you may not edit another user\'s profile')
            redirect(came_from)
        
    @expose(config.profile_template)
    def profile(self, user_id, came_from='/'):
        #self._check_identity(user_id, came_from)
        pylons.c.edit = profileForm
        user_data = self.provider.select(config.users_table, values={'user_id':user_id})[0]
        user_data = dict(user_data)
        user_data['came_from'] = came_from
        user_data['passwordVerification'] = user_data['password']
        # need to pass user_data to the form's value attribute.
        return dict(value=user_data)
    
    @expose()
    def edit_profile(self, **kw):
        user_id = kw.get('user_id')
        came_from = kw.get('came_from')
        self._check_identity(user_id, came_from)
        user_data = self.provider.select(config.users_table, values={'user_id':user_id})[0]
        if user_data['password'] != kw['password']:
            kw['password'] = modify_password(kw['password'])
        self.provider.edit(tableName=config.users_table, values=kw)
        if came_from:
            redirect(came_from)
        redirect(url('/'))

    @expose(config.registration_template)
    def registration(self, **kw):
        pylons.c.form = registrationForm
        return dict(value=kw)

    #need to add stuff here to check for invalid user names (already exists), 
    #provide password complexity algorithms, etc.
    @expose()
    @validate(form=registrationForm, error_handler=registration)
    def register(self, **kw):
        kw['password'] = modify_password(kw['password'])
        print kw
        self.provider.add(config.users_table, values=kw)
        flash('Your account has been successfully created.')
        redirect('registration')

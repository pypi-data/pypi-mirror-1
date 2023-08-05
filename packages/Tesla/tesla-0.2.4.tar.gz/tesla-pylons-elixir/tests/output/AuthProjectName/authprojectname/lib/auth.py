from authkit import permissions
from authprojectname import models as model
from pylons import request

def get_user():
    if 'paste.auth_tkt.current_user' not in request.environ:
        user_id = request.environ.get('REMOTE_USER')
        if user_id:
            request.environ['paste.auth_tkt.current_user'] = model.User.get_by(id = user_id, active = True)
        else:
            request.environ['paste.auth_tkt.current_user'] = None
    return request.environ['paste.auth_tkt.current_user']

def signin(user):
    request.environ['paste.auth_tkt.set_user'](str(user.id))

def signout():
    request.environ['paste.auth_tkt.logout_user']()

class RemoteUser(permissions.Permission):

    def check(self, app, environ, start_response):
        if not get_user() : raise permissions.NotAuthenticatedError
        return app(environ, start_response)

class InGroup(permissions.Permission):

   def __init__(self, group_name):
        self.group_name = group_name 

   def check(self, app, environ, start_response):
        group = model.Group.get_by(name = self.group_name, active = True)
        if group and get_user() in group_members:
            return app(environ, start_response)

class HasPermission(permissions.Permission):

    def __init__(self, permission):
        self.permission = permission

    def check(self, app, environ, start_response):
        user = get_user()
        if user and user.has_permission(self.permission):
            return app(environ, start_response)
        raise permissions.NotAuthorizedError


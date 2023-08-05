from authprojectname.lib.base import *

class AuthController(BaseController):
    __permission__=permissions.SignedIn()
    __excludes__=['post', 'add_user']
    def index(self):
        return render('/index.mako')
    @authorize(permissions.InGroup('Admins'))
    def post(self):
        return 'ok'
    @authorize(permissions.HasPermission('add_users'))
    def add_user(self):
        return 'ok'
    
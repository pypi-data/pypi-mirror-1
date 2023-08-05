from authprojectname.lib.base import *

class AuthController(BaseController):
    def index(self):
        return render_response('/index.mako')
    @authorize(RemoteUser())
    def post(self):
        return Response('ok')
    @authorize(HasPermission('add_users'))
    def add_user(self):
        return Response('ok')

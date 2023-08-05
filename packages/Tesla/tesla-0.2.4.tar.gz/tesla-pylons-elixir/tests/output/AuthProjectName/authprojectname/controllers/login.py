from authprojectname.lib.base import *
from authprojectname.lib.auth import signin, signout

"""
A stub login controller, with signin and signout methods
"""
class LoginController(BaseController):
    def index(self):
        return Response('login_form')
    def signin(self):
        username = request.params.get('username')
        password = request.params.get('password')
        user = model.User.authenticate(username, password)
        if user:
            signin(user)
            redirect_to('/')
        else:
            redirect_to(action = 'index')
    def signout(self):
        signout()
        redirect_to(action = 'login')
 
        
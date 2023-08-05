from authprojectname.lib.base import *
from authprojectname.lib.auth import login, logout

class LoginController(BaseController):

    "A stub example login controller, with login and logout methods"

    def index(self):
        # add your login form here
        return 'login_form'

    def signin(self):
        username = request.params.get('username')
        password = request.params.get('password')
        try:
            user = model.User.authenticate(username, password)
            login(user)
            redirect_to('/')
        except model.NotAuthenticated:
            redirect_to(action='index')

    def signout(self):
        logout()
        redirect_to(action='index')
 
        
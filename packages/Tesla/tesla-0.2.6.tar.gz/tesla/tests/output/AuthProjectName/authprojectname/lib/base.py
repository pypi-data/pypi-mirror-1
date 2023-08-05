from pylons import Response, c, g, cache, request, session
from pylons.controllers import WSGIController
from pylons.decorators import jsonify, validate
from pylons.templating import render
from pylons.helpers import abort, redirect_to, etag_cache
from pylons.i18n import N_, _, ungettext
from authprojectname.lib.auth import get_user, redirect_to_login
from authprojectname.lib.helpers import get_object_or_404
from authprojectname.lib.decorators import authorize
import authprojectname.lib.permissions as permissions
import authprojectname.model as model
import authprojectname.lib.helpers as h

class BaseController(WSGIController):
    __model__ = None
    __permission__ = None
    __excludes__ = []
    
    def __call__(self, environ, start_response):
        # Refresh database session
        model.resync()
        # Insert any code to be run per request here. The Routes match
        # is under environ['pylons.routes_dict'] should you want to check
        # the action or route vars here
        return WSGIController.__call__(self, environ, start_response)

    def __before__(self):
        self._check_action()
        self._load_model()
        self._authorize()
        self._context()

    def _load_model(self):
        """
        If __model__ variable is set will automatically load model instance into context
        if "id" is in Routes. The name used in the context is the same name as the model
        (in lowercase); otherwise you can use the __name__ attribute. 
        """ 
        if self.__model__:
            routes_id = request.environ['pylons.routes_dict']['id']
            if routes_id:
                instance = get_object_or_404(self.__model__, id=routes_id)
                name = getattr(self, '__name__', self.__model__.__name__.lower())
                setattr(c, name, instance)

    def _context(self):
        """
        Put your common context variables in here
        """

    def _check_action(self):
        # do a check for action: otherwise NotImplemented error raised
        action = request.environ['pylons.routes_dict']['action']
        if not hasattr(self, action):
            abort(404)
        
    def _authorize(self):
        # add user to context for convenience
        c.auth_user = get_user()
        if self.__permission__ and \
            request.environ['pylons.routes_dict']['action'] not in self.__excludes__ and \
            not self.__permission__.check():
            redirect_to_login()

# Include the '_' function in the public names
__all__ = [__name for __name in locals().keys() if not __name.startswith('_') \
           or __name == '_']

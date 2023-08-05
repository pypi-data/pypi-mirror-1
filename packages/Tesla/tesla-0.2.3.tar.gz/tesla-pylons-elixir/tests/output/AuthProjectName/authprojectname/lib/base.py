from pylons import Response, c, g, cache, request, session
from pylons.controllers import WSGIController
from pylons.decorators import jsonify, validate
from pylons.templating import render, render_response
from pylons.helpers import abort, redirect_to, etag_cache
from pylons.i18n import N_, _, ungettext
from authkit.pylons_adaptors import authorize
from authprojectname.lib.auth import get_user, RemoteUser, InGroup, HasPermission
from authprojectname.lib.helpers import get_object_or_404
import authprojectname.models as model
import authprojectname.lib.helpers as h


class BaseController(WSGIController):
    def __call__(self, environ, start_response):
        # Refresh database session
        model.resync()
        # Insert any code to be run per request here. The Routes match
        # is under environ['pylons.routes_dict'] should you want to check
        # the action or route vars here
        return WSGIController.__call__(self, environ, start_response)

# Include the '_' function in the public names
__all__ = [__name for __name in locals().keys() if not __name.startswith('_') \
           or __name == '_']

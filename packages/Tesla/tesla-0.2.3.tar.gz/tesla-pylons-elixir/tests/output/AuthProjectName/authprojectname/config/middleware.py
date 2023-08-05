from paste.cascade import Cascade
from paste.urlparser import StaticURLParser
from paste.registry import RegistryManager
from paste.deploy.config import ConfigMiddleware
from paste.deploy.converters import asbool

from pylons.error import error_template
from pylons import config
from pylons.middleware import ErrorHandler, ErrorDocuments, StaticJavascripts, error_mapper
import pylons.wsgiapp

from authprojectname.config.environment import load_environment
import authprojectname.lib.helpers
import authprojectname.lib.app_globals as app_globals

from authkit import authenticate

def make_app(global_conf, full_stack=True, **app_conf):
    """Create a WSGI application and return it
    
    global_conf is a dict representing the Paste configuration options, the
    paste.deploy.converters should be used when parsing Paste config options
    to ensure they're treated properly.
    """
    # Load our Pylons configuration defaults
    load_environment(global_conf, app_conf)
    
    # Load our default Pylons WSGI app and make g available
    app = pylons.wsgiapp.PylonsApp(helpers=authprojectname.lib.helpers,
                                   g=app_globals.Globals)
    app = ConfigMiddleware(app, config._current_obj())
    
    # YOUR MIDDLEWARE
    # Put your own middleware here, so that any problems are caught by the error
    # handling middleware underneath
    
    # If errror handling will be handled by middleware for multiple apps, you
    # will want to set full_stack = False in your config file so that it can
    # catch the problems.
    if asbool(full_stack):
        # Error Handling
        app = ErrorHandler(app, global_conf, error_template=error_template, **config['pylons.errorware'])
    
        # Authentication
        app = authenticate.middleware(app, app_conf)

        # Display error documents for 401, 403, 404 status codes (if debug is disabled also
        # intercepts 500)
        app = ErrorDocuments(app, global_conf, mapper=error_mapper, **app_conf)
    
    # Establish the Registry for this application
    app = RegistryManager(app)
    
    static_app = StaticURLParser(config['pylons.paths']['static_files'])
    javascripts_app = StaticJavascripts()
    app = Cascade([static_app, javascripts_app, app])
    return app

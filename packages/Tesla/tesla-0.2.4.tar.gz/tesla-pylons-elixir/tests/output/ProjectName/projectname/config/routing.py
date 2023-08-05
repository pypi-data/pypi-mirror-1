"""Routes configuration

The more specific and detailed routes should be defined first so they may take
precedent over the more generic routes. For more information refer to the
routes manual at http://routes.groovie.org/docs/
"""
from pylons import config
from routes import Mapper

def make_map():
    map = Mapper(directory=config['pylons.paths']['controllers'],
                 always_scan=config['debug'])

    # The ErrorController route (handles 404/500 error pages): it should likely
    # stay at the top to ensure that it can always be resolved
    map.connect('error/:action/:id', controller='error')

    # CUSTOM ROUTES HERE

    map.connect(':controller/:action/:id')
    map.connect('*url', controller='template', action='view')

    return map

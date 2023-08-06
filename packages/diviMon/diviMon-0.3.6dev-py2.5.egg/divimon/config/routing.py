"""Routes configuration

The more specific and detailed routes should be defined first so they
may take precedent over the more generic routes. For more information
refer to the routes manual at http://routes.groovie.org/docs/
"""
from pylons import config
from routes import Mapper

def make_map():
    """Create, configure and return the routes Mapper"""
    base_url = config['base_url']
    map = Mapper(directory=config['pylons.paths']['controllers'],
                 always_scan=config['debug'])

    # The ErrorController route (handles 404/500 error pages); it should
    # likely stay at the top, ensuring it can always be resolved
    #map.connect('error/:action/:id', controller='error')
    #map.connect('%s/error/:action/:id' % base_url, controller='error')

    # CUSTOM ROUTES HERE

    map.connect('error', controller='index', action='error')
    map.connect('login', controller='index', action='login')
    map.connect('logout', controller='index', action='logout')
    map.connect('', controller='index', action='index')
    map.connect(':controller/:action/:id')
    map.connect('*url', controller='template', action='view')
    map.connect('%s/*url' % base_url, controller='template', action='view')

    return map

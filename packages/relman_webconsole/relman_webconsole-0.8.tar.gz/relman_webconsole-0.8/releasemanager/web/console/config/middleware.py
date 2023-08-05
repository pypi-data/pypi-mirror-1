from paste import httpexceptions
from paste.cascade import Cascade
from paste.urlparser import StaticURLParser
from paste.registry import RegistryManager
from paste.deploy.config import ConfigMiddleware, CONFIG
from paste.deploy.converters import asbool

from pylons.error import error_template
from pylons.middleware import ErrorHandler, ErrorDocuments, StaticJavascripts, error_mapper
import pylons.wsgiapp

from releasemanager.web.console.config.environment import load_environment
import releasemanager.web.console.lib.helpers
#import releasemanager.web.console.lib.app_globals as app_globals

class Globals(object):

    def __init__(self, global_conf, app_conf, **extra):
        pass
        
    def __del__(self):
        pass



def make_app(global_conf, full_stack=True, **app_conf):
    """Create a WSGI application and return it
    
    global_conf is a dict representing the Paste configuration options, the
    paste.deploy.converters should be used when parsing Paste config options
    to ensure they're treated properly.
    
    """
    # Setup the Paste CONFIG object
    CONFIG.push_process_config({'app_conf': app_conf,
                                'global_conf': global_conf})

    # Load our Pylons configuration defaults
    config = load_environment(global_conf, app_conf)
    config.init_app(global_conf, app_conf, package='releasemanager.web.console')
    # Setup Mako Template Engine
    myghty = config.template_engines.pop()
    config.add_template_engine('mako', 'jackal.templates', {})
    config.template_engines.append(myghty)

        
    # Load our default Pylons WSGI app and make g available
    app = pylons.wsgiapp.PylonsApp(config, helpers=releasemanager.web.console.lib.helpers,
                                   g=Globals)
    g = app.globals
    app = ConfigMiddleware(app, {'app_conf':app_conf,
        'global_conf':global_conf})
    
    # YOUR MIDDLEWARE
    # Put your own middleware here, so that any problems are caught by the error
    # handling middleware underneath
    
    # If errror handling and exception catching will be handled by middleware
    # for multiple apps, you will want to set full_stack = False in your config
    # file so that it can catch the problems.
    if asbool(full_stack):
        # Change HTTPExceptions to HTTP responses
        app = httpexceptions.make_middleware(app, global_conf)
    
        # Error Handling
        app = ErrorHandler(app, global_conf, error_template=error_template, **config.errorware)
    
        # Display error documents for 401, 403, 404 status codes (if debug is disabled also
        # intercepts 500)
        app = ErrorDocuments(app, global_conf, mapper=error_mapper, **app_conf)
    
    # Establish the Registry for this application
    app = RegistryManager(app)
    
    static_app = StaticURLParser(config.paths['static_files'])
    javascripts_app = StaticJavascripts()
    app = Cascade([static_app, javascripts_app, app])
    return app

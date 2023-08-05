from pylons import Response, c, g, cache, request, session
from pylons.controllers import WSGIController
from pylons.decorators import jsonify, validate
from pylons.templating import render, render_response
from pylons.helpers import abort, redirect_to, etag_cache
from pylons.i18n import N_, _, ungettext
import releasemanager.web.console.models as model
import releasemanager.web.console.lib.helpers as h

class BaseController(WSGIController):

    def __before__(self):
        if not self.__template_base__ == "/login" and not session.get('authenticated'):
            return redirect_to('/login')
        
    
    __template_base__ = ""

    def render_from_base(self, fname):
        _render_template_file = "%s/%s" % (self.__template_base__, fname)
        if self.__template_base__ == "":
            _render_template_file = "%s" % fname
        return render_response(_render_template_file)
    
    
    def __call__(self, environ, start_response):
        # Insert any code to be run per request here. The Routes match
        # is under environ['pylons.routes_dict'] should you want to check
        # the action or route vars here
        return WSGIController.__call__(self, environ, start_response)

# Include the '_' function in the public names
__all__ = [__name for __name in locals().keys() if not __name.startswith('_') \
           or __name == '_']

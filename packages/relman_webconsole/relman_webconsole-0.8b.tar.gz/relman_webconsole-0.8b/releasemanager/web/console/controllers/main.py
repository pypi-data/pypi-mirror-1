from releasemanager.web.console.lib.base import *

class MainController(BaseController):
    __template_base__ = "/main"
    
    def index(self):
        return self.render_from_base('index.html')

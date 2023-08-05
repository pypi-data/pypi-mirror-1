from releasemanager.web.console.lib.base import g
from releasemanager.auth import PluginBase

class AdminPlugin(PluginBase):
    def authenticate(self, credentials):
        username = credentials.get('username')
        password = credentials.get('password')
        admin_name = g.pylons_config.app_conf.get('releasemanager.admin_name')
        admin_pass = g.pylons_config.app_conf.get('releasemanager.admin_pass')
        if username == admin_name and username is not None:
            if password == admin_pass and password is not None:
                return True
        return False

    def authorize(self, credentials):
        True



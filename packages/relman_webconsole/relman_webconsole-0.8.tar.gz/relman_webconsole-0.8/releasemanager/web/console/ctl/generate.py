import os, sys
import shutil
from releasemanager.ctl.generate import BaseAppCreator, PluginCreator

TEMPLATE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "templates")


class WebConsoleCreator(BaseAppCreator):
    """a manager creator"""
    def generate(self):
        self.base_build()
        data_out_dir = "%s%sdata" % (self.build_path, os.sep)
        if not os.path.isdir(data_out_dir):
            os.mkdir(data_out_dir)
        ini_template = "development.ini"
        shutil.copy("%s/%s" % (TEMPLATE_DIR, ini_template), "%s/%s" % (self.build_path, ini_template))
        

class WebPluginCreator(PluginCreator):
    plugins = {
        "auth" : {
            "simpleauth" : ["simpleauth.py", "plugin_auth_simpleauth.xml"],
            "admin" : ["admin.py", "plugin_auth_admin.xml"],
        }
    }

import os.path
from releasemanager.web.console.lib.base import *
from releasemanager.auth import AuthMaker

from releasemanager.web.console.widgets.login import LoginFieldSet

from toscawidgets.mods.pylonshf import render_response as tw_render_response
from toscawidgets.api import WidgetBunch
from formencode import Invalid

login_field_set = LoginFieldSet()


class LoginController(BaseController):
    __template_base__ = "/login"

    auth = AuthMaker(g.pylons_config.app_conf['releasemanager.auth_plugin'], os.path.join(g.pylons_config.app_conf['releasemanager.plugin_conf'], "auth"))

    def index(self):
        c.w = WidgetBunch()
        c.w.fields = login_field_set
        return tw_render_response("/login/form.html")


    def login(self):
        results = {}
        widget_fields = {}
        for child in login_field_set.children:
            widget_fields[child.name] = child
        field_names = widget_fields.keys()
        for field_name in field_names:
            post_value = request.params.get(field_name)
            results[field_name] = post_value
            field = widget_fields[field_name]
            if hasattr(field, 'validator'):
                try:
                    results[field_name] = field.validator.to_python(post_value)
                except Invalid:
                    pass
            else:
                results[field_name] = post_value
        authenticated = self.auth.authenticate(results)
        if authenticated:
            session['credentials'] = results
            session['authenticated'] = True
            session.save()
            return redirect_to("/managers")
        else:
            c.w = WidgetBunch()
            c.w.fields = login_field_set
            c.flash = "Invalid Login."
            return self.render_from_base('form.html')
            
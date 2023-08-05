from formencode import validators
from formencode.schema import Schema

from toscawidgets.api import WidgetsList, CSSSource, JSSource
from toscawidgets.js import js_function
from toscawidgets.widgets import forms as wf


class FilteringSchema(Schema):
    filter_extra_fields = True
    allow_extra_fields = True


class LoginFieldSet(wf.ListFieldSet):
    class fields(WidgetsList):
        username = wf.TextField("username", label="Username", validator=validators.String)
        password = wf.PasswordField("password", label="Password", validator=validators.String)
        
    validator = FilteringSchema
    include_dynamic_js_calls = True
    

from formencode import validators
from formencode.schema import Schema

from toscawidgets.api import WidgetsList, CSSSource, JSSource
from toscawidgets.js import js_function
from toscawidgets.widgets import forms as wf


class FilteringSchema(Schema):
    filter_extra_fields = True
    allow_extra_fields = True


class ReleaseInstallFieldSet(wf.ListFieldSet):
    class fields(WidgetsList):
        trunk = wf.CheckBox("trunk", label="Use Trunk?", validator=validators.Bool)
        branch = wf.TextField("branch", label="Branch", validator=validators.String)
        tag = wf.TextField("tag", label="Tag", validator=validators.String)
        revision = wf.TextField("revision", label="Revision", validator=validators.Int)
        
    validator = FilteringSchema
    include_dynamic_js_calls = True
    

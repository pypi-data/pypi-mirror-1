from releasemanager.web.console.lib.base import *
from releasemanager.web.console.models import managers
from releasemanager.web.console.widgets.managers import ReleaseInstallFieldSet

from toscawidgets.mods.pylonshf import render_response as tw_render_response
from toscawidgets.api import WidgetBunch
from formencode import Invalid

release_install_fields = ReleaseInstallFieldSet()

class ManagersController(BaseController):
    """REST Controller for interacting with ReleaseManager manager instances"""
    
    __template_base__ = "/managers"
    
    @property
    def manager_inspector(self):
        configured_managers = g.pylons_config.app_conf['releasemanager.managers']
        manager_inspector = managers.ManagerInspector(configured_managers)
        return manager_inspector
   

    def index(self, format='html'):
        """GET /: All items in the collection."""
        c.managers = self.manager_inspector.managers
        return self.render_from_base("index.html")


    def list_projects(self, id, format='html'):
        c.manager = self.manager_inspector.get_manager(id)
        c.projects = []
        if c.manager:
            c.projects = c.manager.projects
        return self.render_from_base("_list_projects.html")

    def list_installers(self, id, format='html'):
        c.manager = self.manager_inspector.get_manager(id)
        c.installers = []
        if c.manager:
            c.installers = [inst for inst in c.manager.installers.values()]
        return self.render_from_base("_list_installers.html")
    
    def list_environments(self, id, format='html'):
        """list environments valid for a given project"""
        loc, tmp, proj = id.split('[')
        loc = loc.replace(']', '')
        proj = proj.replace(']', '')
        c.manager = self.manager_inspector.get_manager(loc)
        c.project = proj
        all_envs = []
        valid_envs = []
        h.observe_field
        # we need to look through our registered projects
        # check what named targets are associated
        # and then check through our list of named installers
        # and see which ones have an environment that matches at least one
        # of the nts's.  all must be matched before the project is valid
        check_proj = None
        named_targets = []
        for p in c.manager.projects:
            p_name = p.keys()[0]
            if p_name.lower() == proj.lower():
                check_proj = p_name
                named_targets = p[p_name]
                break
        
        has_builder = c.manager.has_builder_for_project(check_proj)
            
        all_from_installer, valid_from_installer = c.manager.installer_envs_for_targets(named_targets)
        for afi in all_from_installer:
            if afi not in all_envs:
                all_envs.append(afi)
        for vfi in valid_from_installer:
            if vfi not in valid_envs:
                valid_envs.append(vfi)
        if not has_builder:
            valid_envs = []
        c.environments = {'all' : all_envs, 'valid' : valid_envs}     
        return self.render_from_base("_list_environments.html")
            

    def query_transaction(self, id, format='html'):
        loc, tmp, trans_id = id.split('[')
        loc = loc.replace(']', '')
        trans_id = int(trans_id.replace(']', ''))
        c.manager = self.manager_inspector.get_manager(loc)
        c.transaction_status = c.manager.query_transaction(trans_id)
        return self.render_from_base('_install_status.html')
        

    def list_builders(self, id, format='html'):
        c.manager = self.manager_inspector.get_manager(id)
        c.builders = []
        if c.manager:
            c.builders = [inst for inst in c.manager.project_builders.values()]
        return self.render_from_base("_list_builders.html")


    def make_install_form(self, id, format='html'):
        loc, proj, env = id.split('[')
        loc = loc.replace(']', '')
        proj = proj.replace(']', '')
        env = env.replace(']', '')
        c.manager = self.manager_inspector.get_manager(loc)
        c.project = proj
        c.environment = env
        c.w = WidgetBunch()
        c.w.fields = release_install_fields
        return tw_render_response("/managers/form.html")
    

    def install(self):
        c.manager = self.manager_inspector.get_manager(request.params.get('manager_id'))
        credentials = session['credentials']
        results = {}
        widget_fields = {}
        for child in release_install_fields.children:
            widget_fields[child.name] = child
        field_names = ['project', 'manager_id', 'env'] + widget_fields.keys()
        for field_name in field_names:
            post_value = request.params.get(field_name)
            if not post_value:
                continue
            results[field_name] = post_value
            if not field_name in widget_fields:
                continue
            field = widget_fields[field_name]
            if hasattr(field, 'validator'):
                try:
                    results[field_name] = field.validator.to_python(post_value)
                except Invalid:
                    pass
            else:
                results[field_name] = post_value
        request_data = {}
        for elem in ['trunk', 'branch', 'tag', 'revision', 'project', 'env']:
            if elem in results:
                request_data[elem] = results[elem]

        trans_id = c.manager.install_project(credentials, request_data)
        c.transaction_id = trans_id
        return self.render_from_base("_install_check_status.html")
        
    

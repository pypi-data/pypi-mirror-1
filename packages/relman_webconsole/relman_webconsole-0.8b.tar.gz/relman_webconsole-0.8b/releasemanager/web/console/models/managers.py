import xmlrpclib
from base import RelmanModelBase
from installers import Installer
from builders import Builder

class Manager(RelmanModelBase):
    def __init__(self, location):
        super(Manager, self).__init__(location)
        # doing this rather than making it a property
        # because i don't want to pass in an object to a render template
        # that will, at render time, be making xmlrpclib calls
        self.build_registrations()

    def build_registrations(self):
        if not self.connected:
            return None
        s = xmlrpclib.ServerProxy(self.xmlrpc_url)
        self.registrations = s.report_registrations()
    
    @property
    def projects(self):
        if not self.registrations.get('projects', None):
            return {}
        projects = self.registrations.get('projects')
        return projects


    @property
    def installers(self):
        if not self.registrations.get('release_installer', None):
            return {}
        release_installer_data = self.registrations.get('release_installer')
        release_installers = {}
        for rid in release_installer_data:
            release_installers[rid] = Installer(release_installer_data[rid])
        return release_installers


    @property
    def all_builders(self):
        if not self.registrations.get('build_host', None):
            return {}
        release_builder_data = self.registrations.get('build_host')
        release_builders = {}
        for rbd in release_builder_data:
            release_builders[rbd] = Builder(release_builder_data[rbd])
        return release_builders

    
    @property
    def project_builders(self):
        project_builders = {}
        for loc, b in self.all_builders.items():
            builds_ours = False
            for proj in b.projects:
                proj = proj.replace("release_builder_", "")
                if proj in self.projects:
                    builds_ours = True
            if builds_ours:
                project_builders[loc] = b
        return project_builders

    
    def install_project(self, credentials, request_data):
        transaction_id = None
        if not self.connected:
            return transaction_id
        s = xmlrpclib.ServerProxy(self.xmlrpc_url)
        request_data['action'] = 'install'
        transaction_id = s.request_action(credentials, request_data)
        return transaction_id
    
    
    def query_transaction(self, trans_id):
        status = "UNKNOWN"
        if self.connected:
            s = xmlrpclib.ServerProxy(self.xmlrpc_url)
            status = s.query_transaction(trans_id)
        return status

    
    def has_builder_for_project(self, project):
        self.build_registrations()
        builds_ours = False
        for b in self.all_builders.values():
            for proj in b.projects:
                proj = proj.replace("release_builder_", "")
                if proj == project:
                    if b.connected:
                        builds_ours = True
                        break
        return builds_ours


    def installer_envs_for_targets(self, named_targets):
        self.build_registrations()
        all_envs = []
        valid_envs = []
        found_targets = {}
        for inst in self.installers.values():
            for env in inst.environments:
                if env not in all_envs:
                    all_envs.append(env)
            for env, tgs in inst.targets.items():
                if not env in found_targets:
                    found_targets[env] = []
                for t in tgs:
                    if not t in found_targets[env]:
                        found_targets[env].append(t)
                    if t in named_targets:
                        if env not in valid_envs:
                            if inst.connected:
                                valid_envs.append(env)
        # now we look through the envs so far marked as valid
        # and check that the named target requirements have been met
        # in total for each env, otherwise remove it from valid envs
        for env in valid_envs:
            found_all_for_env = True
            for nt in named_targets:
                if not nt in found_targets[env]:
                    found_all_for_env = False
                    break
            if not found_all_for_env:
                valid_envs.remove(env)
        return (all_envs, valid_envs)
    

class ManagerInspector(object):
    """manager inspector class"""
    def __init__(self, managers):
        self.managers = managers
    
    def _build_managers(self, managers):
        """obliterates the cache, checks the configured ones, if they're alive, uses them"""
        self._managers = []
        mgrs = managers.split(",")
        for mgr in mgrs:
            self._managers.append(Manager(mgr))
    
    def getManagers(self):
        return self._managers
    
    def setManagers(self, managers):
        self._build_managers(managers)
    
    managers = property(getManagers, setManagers)
    
    def get_manager(self, loc):
        manager = None
        for mgr in self.managers:
            if mgr.location.lower() == loc.lower():
                manager = mgr
                break
        return manager


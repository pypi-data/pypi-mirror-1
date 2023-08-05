from base import RelmanModelBase

class Installer(RelmanModelBase):
    """installer object"""
    def __init__(self, data):
        host = data.get('host')
        port = data.get('port')
        super(Installer, self).__init__("%s:%s" % (host, port))
        self._installables = data.get('payload')
        
    
    @property
    def environments(self):
        if self._installables:
            installables = self._installables.keys()
            installables.sort()
            return installables
        return []
        
    @property
    def targets(self):
        if not self._installables:
            return {}
        return self._installables
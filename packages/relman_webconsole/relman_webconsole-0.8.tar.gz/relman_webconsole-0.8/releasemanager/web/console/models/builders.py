from base import RelmanModelBase

class Builder(RelmanModelBase):
    """builder object"""
    def __init__(self, data):
        host = data.get('host')
        port = data.get('port')
        super(Builder, self).__init__("%s:%s" % (host, port))
        self.projects = data.get('payload')
    
    
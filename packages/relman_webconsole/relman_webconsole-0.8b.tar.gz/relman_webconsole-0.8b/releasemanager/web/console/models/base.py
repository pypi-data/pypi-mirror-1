import socket, xmlrpclib


class RelmanModelBase(object):
    """base class for releasemanager model objects"""
    
    def __init__(self, location):
        self.location = location
        self.xmlrpc_url = "http://%s/RPC2" % self.location
        # test once, leave it as a property
        # forcing it to actually run the method at render time is dumb
        self.connected = self.test_connected()
    
    def test_connected(self):
        s = socket.socket()
        connected = True
        host, port = self.location.split(":")
        try:
            s.connect((host, int(port)))
        except:
            connected = False
        return connected
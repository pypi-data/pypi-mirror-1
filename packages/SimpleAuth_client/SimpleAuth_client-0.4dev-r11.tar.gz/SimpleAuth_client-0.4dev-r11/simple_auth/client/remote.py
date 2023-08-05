import socket, xmlrpclib

class ConnectionError(Exception):
    """if we aren't connected"""

class RemoteAuth(object):
    def __init__(self, server, port):
        self.server = server
        self.port = int(port)
        self.remote_url = "http://%s:%s/RPC2" % (server, port)

    @property
    def connected(self):
        s = socket.socket()
        connected = True
        try:
            s.connect((self.server, self.port))
        except:
            connected = False
        return connected     
    
    
    def authenticate(username, password, crypt=None, plugin=None, resource=None):
        if not self.connected:
            raise ConnectionError("Not connected to %s, unable to authenticate")
        s = xmlrpclib.ServerProxy(self.remote_url)
        if plugin and not crypt:
            crypt = ('', '')
        if resource:
            plugin = ''
            crypt = ('', '')
        if crypt and not plugin:
            return s.authenticate(username, password, crypt)
        elif plugin:
            return s.authenticate(username, password, crypt, plugin)
        elif resource:
            return s.authenticate(username, password, crypt, plugin, resource)
        return s.authenticate(username, password)

    def authorize(service_name, username, rolename, plugin=None, resource=None):
        if not self.connected:
            raise ConnectionError("Not connected to %s, unable to authenticate")
        s = xmlrpclib.ServerProxy(self.remote_url)
        if plugin:
            return s.authorize(service_name, username, rolename, plugin)
        elif resource:
            return s.authorize(service_name, username, rolename, '', resource)
        return s.authorize(service_name, username, rolename)

    
    def get_roles_for_user(self, service_name, username, resource=None):
        if not self.connected:
            raise ConnectionError("Not connected to %s, unable to authenticate")
        s = xmlrpclib.ServerProxy(self.remote_url)
        if resource:
            return s.get_roles_for_user(service_name, username, resource_name)
        return s.get_roles_for_user(service_name, username)
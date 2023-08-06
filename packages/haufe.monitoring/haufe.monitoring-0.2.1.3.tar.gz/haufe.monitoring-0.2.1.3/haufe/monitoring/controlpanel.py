################################################################
# haufe.monitoring
# (C) 2009, Haufe Mediengruppe, Written by Andreas Jung
################################################################

from datetime import datetime
import logging
import socket

import Globals
from OFS.SimpleItem import SimpleItem
from AccessControl import ClassSecurityInfo
from BTrees.OOBTree import OOBTree
from App.config import getConfiguration

LOG = logging.getLogger('haufe.monitoring')
ControlPanelId = 'haufe.monitoring control panel'

class Server(object):

    def __init__(self, ip, port, hostname):
        self.ip = ip
        self.port = port
        self.hostname = hostname
        self.url = 'http://%s:%d' % (self.hostname, self.port)
        self.started = datetime.now()
        self.started_str = self.started.strftime('%d.%m.%y %H:%M:%S')

    def __str__(self):
        return ('%s(%s)' % (self.__class__.__name__, self.__dict__))

class ControlPanel(SimpleItem):
    """ haufe.monitoring controlpanel integration """
        
    meta_type = 'HaufeMonitoring ControlPanel'
    id = title = ControlPanelId
    title = 'haufe.monitoring control panel'
    
    security = ClassSecurityInfo()
    security.setDefaultAccess(True)
    
    # Configuration properties
    _properties = ()

    def unregisterZopeInstance(self, host, port):
        try:
            del self.servers[(host, port)]
            LOG.info('Unregistered host %s:%d' % (host, port))
        except KeyError:
            pass

    def registerZopeInstance(self):                 

        if not hasattr(self, 'servers'):
            self.servers = OOBTree()

        port_base = getConfiguration().port_base or 0

        # We can habe multiple servers (although pretty uncommon).
        # Choose the one with the lowest port.
        from ZServer.HTTPServer import zhttp_handler

        candidates =  list()
        servers = getConfiguration().servers
        servers.sort(lambda x,y: cmp(x.port, y.port))
        for server in servers:
            try:            
                if isinstance(server.handlers[0], zhttp_handler):
                    candidates.append(server)
            except:
                pass

        if candidates:
            candidate = candidates[0]
            ip_address = candidate.server_port 

            hostname = socket.gethostname()
            ip = socket.gethostbyname(hostname)
            port = port_base + ip_address
            server = Server(ip, port, hostname)
            LOG.info('Registered %s' % server)
            self.servers[(hostname, port)] = server

    def getServers(self):
        servers = list(self.servers.values())
        return servers

Globals.InitializeClass(ControlPanel)

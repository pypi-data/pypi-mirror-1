###############################################################
# haufe.monitoring
# (C) 2009, Haufe Mediengruppe, Written by Andreas Jung
################################################################

import os
import urllib
import urllib2
import demjson
import socket
import logging

from Products.Five.browser import BrowserView
from Globals import InitializeClass

from zope.app.pagetemplate.viewpagetemplatefile import ViewPageTemplateFile
from haufe.monitoring.controlpanel import ControlPanelId
from haufe.monitoring.network import isRequestAllowed

LOG = logging.getLogger('haufe.monitoring')

class MonitorView(BrowserView):

    template = ViewPageTemplateFile('monitor.pt')

    def __call__(self):
        return self.template()

    def getServers(self):
        return self.context.Control_Panel[ControlPanelId].getServers()

    def getStats(self):

        stats = dict()
        for server in self.getServers():

            # the remote URL for obtaining the system stats
            url = 'http://%s:%d/@@system_information' % (server.hostname, server.port)

            stats[(server.hostname, server.port)] = None
            try:
                socket.setdefaulttimeout(5)
                json_data = urllib2.urlopen(url).read()
                stats[(server.hostname, server.port)] = demjson.decode(json_data)
                socket.setdefaulttimeout(None)
            except urllib2.URLError, e:
                socket.setdefaulttimeout(None)
                continue

        return stats

    def remove_hosts(self):

        for hostSpec in self.request.get('hosts', []):
            host, port = hostSpec.split(':')
            self.context.Control_Panel[ControlPanelId].unregisterZopeInstance(host, int(port))
        return self.request.response.redirect('/@@monitor')

    def restart(self):
        """ Restart Zope instances """

        for hostSpec in self.request.get('hosts', []):
            host, port = hostSpec.split(':')
            url = 'http://%s:%s/Control_Panel/manage_restart' % (host, port)
            request = urllib2.Request(url)
            response = urllib2.urlopen(request)
            answer = response.read()

    def shutdown(self):
        """ Shutdown Zope instances """

        for hostSpec in self.request.get('hosts', []):
            host, port = hostSpec.split(':')
            url = 'http://%s:%s/Control_Panel/manage_shutdown' % (host, port)
            request = urllib2.Request(url)
            response = urllib2.urlopen(request)
            answer = response.read()

InitializeClass(MonitorView)

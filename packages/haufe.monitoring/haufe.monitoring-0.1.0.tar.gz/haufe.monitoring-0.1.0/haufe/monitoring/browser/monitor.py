###############################################################
# haufe.monitoring
# (C) 2009, Haufe Mediengruppe, Written by Andreas Jung
################################################################

import urllib
import urllib2
import demjson

from Products.Five.browser import BrowserView
from Globals import InitializeClass

from zope.app.pagetemplate.viewpagetemplatefile import ViewPageTemplateFile
from haufe.monitoring.controlpanel import ControlPanelId

class MonitorView(BrowserView):

    template = ViewPageTemplateFile('monitor.pt')

    def __call__(self):
        return self.template()

    def getServers(self):
        return self.context.Control_Panel[ControlPanelId].getServers()

    def getStats(self):

        stats = dict()
        for server in self.getServers():
            url = 'http://%s:%d/@@system_information' % (server.hostname, server.port)
            stats[(server.hostname, server.port)] = None
            try:
                json_data = urllib2.urlopen(url).read()
                stats[(server.hostname, server.port)] = demjson.decode(json_data)
            except urllib2.URLError:
                continue
        return stats

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

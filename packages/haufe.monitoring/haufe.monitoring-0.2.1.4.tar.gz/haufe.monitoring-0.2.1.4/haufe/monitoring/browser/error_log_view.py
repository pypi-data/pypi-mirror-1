################################################################
# haufe.monitoring
# (C) 2009, Haufe Mediengruppe, Written by Andreas Jung
################################################################

import urllib2
import demjson

from Products.Five.browser import BrowserView
from Globals import InitializeClass

from zope.app.pagetemplate.viewpagetemplatefile import ViewPageTemplateFile
from haufe.monitoring.network import isRequestAllowed


class ErrorLogView(BrowserView):

    template = ViewPageTemplateFile('error_log_view.pt')

    def __call__(self):
        return self.template()

    def collect_error_logs(self):

        isRequestAllowed(self.request)

        result = list()
        for hostSpec in self.request.get('hosts', []):
            host, port = hostSpec.split(':') # host:port
            url = 'http://%s:%s/@@get_error_logs' % (host, port)
            json_data = urllib2.urlopen(url).read()
            data = demjson.decode(json_data)
            if data:
                data = data[0]
                data['host'] = host
                data['port'] = port
                result.append(data)
        result.sort(lambda x,y: -cmp(x['time'], y['time']))
        return result

InitializeClass(ErrorLogView)

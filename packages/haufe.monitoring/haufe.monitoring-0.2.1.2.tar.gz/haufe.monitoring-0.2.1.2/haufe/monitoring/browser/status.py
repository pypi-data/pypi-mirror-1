################################################################
# haufe.monitoring
# (C) 2009, Haufe Mediengruppe, Written by Andreas Jung
################################################################

import os
import sys
import demjson
import datetime

from Products.Five.browser import BrowserView
from Globals import InitializeClass
from App.config import getConfiguration

from zope.app.pagetemplate.viewpagetemplatefile import ViewPageTemplateFile
import unix

class StatusView(BrowserView):

    def system_information(self): 
        """ return some system information json-encoded """
        cfg = getConfiguration()
        result = dict()
        result["INSTANCE_HOME"] = cfg.instancehome
        result["port_base"] = cfg.port_base
        result["ip_address"] = cfg.ip_address
        result["debug_mode_cfg"] = cfg.debug_mode
        result["load"] = unix.getLoad()
        result['vmdata_size'] = unix.getVmDataSize()
        result["zserver_threads"] = cfg.zserver_threads
        result['temporary_storage'] = self.context.Control_Panel.Database['temporary']._p_jar.db().getName()
        return demjson.encode(result)

    def get_error_logs(self):
        """ return error_log json-encoded """
        error_log = self.context.error_log
        entries = error_log.getLogEntries()
        for entry in entries:
            entry['time_str'] = datetime.datetime.fromtimestamp(entry['time']).strftime('%d.%m.%y&nbsp;%H:%M:%S')
        entries.sort(lambda x,y: -cmp(x['time'], y['time']))
        return demjson.encode(entries)

InitializeClass(StatusView)

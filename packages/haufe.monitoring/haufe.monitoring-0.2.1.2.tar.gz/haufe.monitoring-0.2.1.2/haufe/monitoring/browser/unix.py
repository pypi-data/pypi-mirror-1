################################################################
# haufe.monitoring
# (C) 2009, Haufe Mediengruppe, Written by Andreas Jung
################################################################

import os

class ProcStatus:
    """
    determine Process Status for a given or current process
    originaly taken from work by Nils Weinzierl (memory profiling in Haufe HRS environment)

    see also 

    http://mail.python.org/pipermail/python-list/2004-June/266257.html
    How to get process info from python

    http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/286222
    Memory usage. 
    """
    
    def __init__(self,procid):
        self.name = 'status'
        self.format = ('f', 5, 1024)
        self.f = file('/proc/%s/status' % procid, 'r', 0)
        self.vars = ('SleepAVG', 'VmPeak', 'Cached', 'MemFree','Threads','VmData')
        
    def extract(self, vars=None):
        self.val = {}
        if not vars:
            vars = self.vars
        self.f.seek(0)
        for line in self.f.readlines():
            l = line.split(':')
            l[1] = l[1].strip()
            if l[0] in vars:
                self.val[l[0]] = l[1]
        return self.val    

def getLoad():
    load = file('/proc/loadavg').read().split()[0]
    return load

def getVmDataSize():
    """returns the virtual Memory needed for the process with the id pid """

    pid = os.getpid()
    try:
        vals = ProcStatus(pid).extract()
        return int(vals['VmData'].replace(' kB',''))
    except:
        return -1

if __name__ == '__main__':
    print getLoad()
    print getVmDataSize()

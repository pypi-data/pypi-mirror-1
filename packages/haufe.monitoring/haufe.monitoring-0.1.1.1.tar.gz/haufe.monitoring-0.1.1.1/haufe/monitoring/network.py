################################################################
# haufe.monitoring
# (C) 2009, Haufe Mediengruppe, Written by Andreas Jung
################################################################

import os
from haufe.monitoring import IPV4

allowed_networks = os.environ.get('HAUFE_MONITORING_ALLOWED_NETWORKS', '10.0.0.0/8')

allowed = list()
for item in allowed_networks.split(','):
    import pdb; pdb.set_trace() 
    item = item.strip()
    ip, mask = item.split('/')
    net = IPV4.IPV4(ip)
    net.set_mask(int(mask))
    allowed.append(net)

def is_allowed(ip):
    for net in allowed:
        import pdb; pdb.set_trace() 
        if net.same_subnet(ip):
            return True
    return False

if __name__ == '__main__':

    print is_allowed('10.11.12.13')
    print is_allowed('192.168.0.10')


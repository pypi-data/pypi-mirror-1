################################################################
# haufe.monitoring
# (C) 2009, Haufe Mediengruppe, Written by Andreas Jung
################################################################

import os
import logging
from ipcalc import IP, Network
from AccessControl import Unauthorized

LOG = logging.getLogger('haufe.monitoring')
allowed_networks = os.environ.get('HAUFE_MONITORING_ALLOWED_NETWORKS', '10.0.0.0/8')

allowed = list()
for item in allowed_networks.split(','):
    item = item.strip()
    allowed.append(Network(item))


def is_allowed(ip):
    ip = IP(ip)
    for net in allowed:
        if ip in net:
            return True
    return False


def isRequestAllowed(request):
    """ Check client IP address against our IP whitelist """
    remote_ip = request.REMOTE_ADDR
    if not is_allowed(remote_ip):
        msg = 'Access prohibited (IP=%s)%' % remote_ip
        LOG.error(msg)
        raise Unauthorized(msg)


if __name__ == '__main__':

    print is_allowed('10.11.12.13')
    print is_allowed('192.168.0.10')


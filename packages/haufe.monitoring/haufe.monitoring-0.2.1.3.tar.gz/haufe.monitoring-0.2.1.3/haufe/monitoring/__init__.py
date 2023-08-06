################################################################
# haufe.monitoring
# (C) 2009, Haufe Mediengruppe, Written by Andreas Jung
################################################################

import transaction
import logging

LOG = logging.getLogger('haufe.monitoring')

def initialize(context): 
    """$ initialize haufe.monitoring """
    from haufe.monitoring.controlpanel import ControlPanel, ControlPanelId

    LOG.debug('Initializing control panel')
    cp = context._ProductContext__app.Control_Panel
    if not ControlPanelId in cp.objectIds():
        monitor = ControlPanel()
        cp._setObject(ControlPanelId, monitor)
        transaction.commit()

    monitor = cp[ControlPanelId]

    LOG.debug('attempt to register this Zope Instance with ControlPanel')
    from ZODB.POSException import ConflictError
    retry_count = 5
    try:
        while retry_count > 0:
            try:
                monitor.registerZopeInstance()
                retry_count = 0
            except ConflictError:
                retry_count -= 1
                LOG.warn('ConflictErorr while registering Zope Instance')
                if retry_count > 0: 
                    continue
                raise # retry action
        LOG.debug('Zope instance successfully registered')
        transaction.commit()
 
    except:
         LOG.error('Failed to register Zope instance', exc_info=True)

    LOG.debug('Starting GIL monitor')
    import gil_monitor
    gil_monitor.start()

    # reconfigure garbage collector
    #  generation 0 GC at "(allocated - freed) == 7.000"; analyse 7.000 objects
    #  generation 1 GC at "(allocated - freed) == 140.000"; analyse 140.000 objects
    #  generation 2 GC at "(allocated - freed) == 1.400.000"; analyse all objects

    LOG.debug('reconfigured garbage collector thresholds')
    import gc
    gc.set_threshold(7000, 20, 10)


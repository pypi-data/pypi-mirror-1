################################################################
# haufe.monitoring
# (C) 2009, Haufe Mediengruppe, Written by Andreas Jung
################################################################



import logging
log = logging.getLogger('haufe.monitoring')

from time import time, sleep
from thread import start_new_thread

_runThread = False

def start():
    global _runThread
    if not _runThread:
        _runThread = True
        start_new_thread(_monitor, ())

def stop():
    global _runThead
    _runThread = False

def _monitor():
    while _runThread:
        start = time()
        sleep(1)
        end = time()
        if end - start >= 2:
            log.warning('1s schedule took %ss' % (end-start))

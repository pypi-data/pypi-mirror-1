Introduction
============

A suite of views for monitoring a set of ZEO clients.

Features
========

* aggregated view of error_logs
* aggregated view of instances, #threads, load and VM data size

Installation
============

* add ``haufe.monitoring`` to the ``eggs`` and ``zcml`` options of your buildout.cfg

* visit the @@monitor view (http://your-site:port/@@monitor)

Configuration
=============

* access to some views is allowed only to a configurable set up ip addresses or networks. By default
  only access from 10.0.0.0/8 is allowed. To configure the whiteliste, you have to set::

    $ export HAUFE_MONITORING_ALLOWED_NETWORKS=192.168.10.0/24,134.96.0.0/16


View
====

``haufe.monitoring`` currently provides the following view:

* the main view ``/@@monitor`` shows a list of all available or unavailable ZEO clients with their IP addess,
  timestamp of their registration, number of worker threads, the CPU load and the vmdata size.
  The button ``Error log`` will display an aggregated view of the /error_log instances of
  all selected hosts. The ``Remove hosts`` button will remove the selected host(s) from the persistent
  hosts registries. 

* the aggregated error_log view ``/@@show_error_log``  will show the /error_log entries of all (selected) hosts sorted
  by time stamp. The ``Details`` button displays the related traceback without having to visit
  the remote machine.


Warning
=======

* There might be open security issues with this module. Please use it for testing or on internal
  servers only. Use it at your own risk.

Todo
====

* tighten security
* deal with ZEO client zombies
* add restart/shutdown code
* support haufe.ztop

Know issue
==========

* the `Details` buttons does seem to work with Firefox 3.5 (related to an incompatiblity with jQueryTools 1.1.x?)


Author
======
Andreas Jung & others, Haufe Mediengruppe


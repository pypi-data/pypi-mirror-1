Introduction
============

``haufe.requestmonitoring`` implements a detailed request logging functionality
on top of the publication events as introduced with Zope 2.12.


Requirements
============

* Zope 2.12.0b2 or higher (or a Zope 2 trunk checkout)

Features
========

Fine resolution request logging
-------------------------------

Used as base for ``ztop`` and ``zanalyse``, i.e. helps to determine the Zope load,
detect long running requests and to analyse the causes of restarts.


The implementation in this module registers subscribers for ``IPubStart`` and
``IPubSuccess/IPubFailure``.  For each of these events, a log entry of the form
``timestamp status request_time type request_id request_info`` is written.

*timestamp* is the current time in the format ``%y%m%dT%H%M%S``.

*status* is ``0`` for ``IPubStart`` events, ``390`` for requests that will
be retried and the result of ``IStatus`` applied to the response otherwise.

*request_time* is ``0`` for ``IPubStart`` events. Otherwise, it will be
the request time in seconds.

*type* is ``+`` for ``IPubStart`` and ``-`` otherwise.

*request_id* is the (process) unique request id.

*request_info* is ``IInfo`` applied to the request.


In addition, a log entry with ``request_info == restarted`` is written when this
logging is activated. Apart from ``request_info`` and ``timestamp`` all other
fields are ``0``. It indicates (obviously) that the server has been restarted.
Following requests get request ids starting with ``1``.


To activate this logging, both ``timelogging.zcml`` must be activated and a
``product-config`` section with name ``timelogging`` must be defined containing the
key ``filebase``.  It specifies the basename of the logfile; ``.<date>`` will be
appended to this base.  Then, ``ITicket``, ``IInfo`` adapters must be defined (e.g.
the one from ``info``). An ``IStatus`` adapter may be defined for response.


Success request logging
-----------------------

This logging is used by ``CheckZope`` to determine the amount of work performed
by Zope (in order not to bother it with monitor probes when it is heavily
active) and to detect an unreasonable error rate.

This logging writes two files ``<base>_good.<date>`` and ``<base>_bad.<date>``.
For each request, a character is writen to either the good or the bad logfile,
depending on whether the request was successful or unsuccessful. This means,
that only the file size matters for these logfiles.

Usually, response codes >= 500 are considered as unsuccessful requests.  You
can register an ``ISuccessFull`` adapter, when you need a different
classification.

To activate this logging, both ``successlogging.zcml`` must be activated and a
``product-config`` section with name ``successlogging`` must be defined containing
the key ``filebase``.  It specifies the basename of the logfiles (represented as
``<base>`` above).

Author
======

Dieter Maurer, Haufe Mediengruppe


License
=======

``haufe.requestmonitoring`` is published under the Zope Public License V 2.1 (ZPL)
See LICENSE.txt.



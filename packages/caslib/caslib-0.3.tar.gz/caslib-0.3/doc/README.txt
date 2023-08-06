..    Copyright (C) 2009
..    Associated Universities, Inc.  Washington DC, USA.
..
..    Copying and distribution of this file, with or without modification,
..    are permitted in any medium without royalty provided the copyright
..    notice and this notice are preserved.  This file is offered as-is,
..    without any warranty.

========
Overview
========

caslib provides a python interface to CAS [#CAS]_.

A validating `httplib.HTTPSConnection`:class: and `urllib2.HTTPSHandler`:class:.


Features
========

* `CASServer.login`:meth:	Generate the login URL to log into a CASsified service
* `CASServer.validate`:meth: 	Check a CAS service ticket (use of |ssl| [#PY-SSL]_ is suggested to validate connection to the server)

* `CASService`:class:		Define a CASsifed service

* `login_to_cas_service`:func: 	Attempt to authenticate to a CAS /login form (may require |lxml| [#PY-LXML]_)

Links
=====

.. [#CAS]	Central Authentication Service	<http://www.jasig.org/cas>
.. [#PY-SSL]	`ssl`:mod: implements certificate validation (included in Python-2.6+)
		<http://pypi.python.org/pypi/ssl>
.. [#PY-LXML]	`lxml`:mod: provides html support
		<http://pypi.python.org/pypi/lxml>

.. |ssl| replace::	`ssl`:mod:
.. |lxml| replace::	`lxml`:mod:


#     Copyright (C) 2009
#     Associated Universities, Inc.  Washington DC, USA.
#
#     This file is part of caslib.
#
#     caslib is free software: you can redistribute it and/or modify it under
#     the terms of the GNU Lesser General Public License as published by the
#     Free Software Foundation, either version 3 of the License, or (at your
#     option) any later version.
#
#     caslib is distributed in the hope that it will be useful, but WITHOUT ANY
#     WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
#     FOR A PARTICULAR PURPOSE.  See the GNU Lesser General Public License for
#     more details.
#
#     You should have received a copy of the GNU Lesser General Public License
#     along with caslib.  If not, see <http://www.gnu.org/licenses/>.

'''Validate certificates and hostnames on https connections with urllib2 and httplib'''

from socket import socket, SOCK_STREAM, getaddrinfo, error as SocketError
from httplib import HTTPSConnection
import urllib2

import logging
import warnings

import new


_ssl_module_message = 'Certificate validation will not be available.  Consider installing http://pypi.python.org/pypi/ssl'
try:
    from ssl import SSLSocket, CERT_NONE, CERT_OPTIONAL, CERT_REQUIRED, SSLError, PROTOCOL_TLSv1

except ImportError, e:
    SSLSocket = None
    warnings.warn('%s: %s' % ( e, _ssl_module_message ), category=Warning, stacklevel=2)


__all__ = ['CertNameMismatchError', 'ValidatingHTTPSConnection']

_log = logging.getLogger(__name__)


class CertNameMismatchError(SSLError):
    def __init__(self, hostname, certnames):
	message = 'Name %r does not match any of these certificate names: %r' % ( hostname, certnames )
	super(CertNameMismatchError, self).__init__(message)
	self.hostname = hostname
	self.certnames = certnames


class ValidatingHTTPSConnection(HTTPSConnection):
    '''Variant of httplib.HTTPSConnection that validates server certificates and checks that the hostname matches the certificate.

    The attributes cert_reqs and ca_certs can be passed to the constructor or
    set on the class as defaults.  They work as they do in the newer ssl
    module (which is required, btw).

    The attribute check_hostname can be passed to the constructor or set on the
    class as defaults.  If the certificate is not validated, this check will
    not be performed.  Default is True.
    '''

    ca_certs = None
    cert_reqs = None
    ssl_version = PROTOCOL_TLSv1
    check_hostname = True

    hostname_matches_cert = None

    def __init__(self, host, port=None, key_file=None, cert_file=None,
		 strict=None, cert_reqs=None, ca_certs=None,
		 check_hostname=None, ssl_version=None):

	if not SSLSocket:
	    raise NotImplementedError(_ssl_module_message)

	HTTPSConnection.__init__(self, host, port=port, key_file=key_file,
	    cert_file=cert_file, strict=strict)
	if ca_certs is not None:
	    self.ca_certs = ca_certs
	if ssl_version is not None:
	    self.ssl_version = ssl_version
	if cert_reqs is not None:
	    self.cert_reqs = cert_reqs
	if self.cert_reqs is None: # Is this logic implemented by the ssl class?
	    self.cert_reqs = self.ca_certs and CERT_REQUIRED or CERT_NONE
	if check_hostname is not None:
	    self.check_hostname = check_hostname

    def _compare_hostname(self, host):
	'''Check whether self.host matches host.

	Matching ignores case, and discards any empty domain name labels.  Wildcards match exactly one label.

	# Basic match
	>>> c = ValidatingHTTPSConnection('foo.bar.quux')
	>>> c._compare_hostname('foo.bar.quux')
	>>> c.hostname_matches_cert
	True

	# Wildcard
	>>> c = ValidatingHTTPSConnection('foo.bar.quux')
	>>> c._compare_hostname('*.bar.quux')
	>>> c.hostname_matches_cert
	True

	# Empty domainname labels
	>>> c = ValidatingHTTPSConnection('foo..bar.quux.')
	>>> c._compare_hostname('foo.bar.quux')
	>>> c.hostname_matches_cert
	True

	# Ignore case
	>>> c = ValidatingHTTPSConnection('FOO.bar.quux')
	>>> c._compare_hostname('foo.bar.quux')
	>>> c.hostname_matches_cert
	True

	# Partial match is not valid
	>>> c = ValidatingHTTPSConnection('foo.bar.quux')
	>>> c._compare_hostname('bar.quux')
	>>> c.hostname_matches_cert

	# Wildcard matches bar, but not foo.bar
	>>> c = ValidatingHTTPSConnection('foo.bar.quux')
	>>> c._compare_hostname('*.quux')
	>>> c.hostname_matches_cert

	# Too short
	>>> c = ValidatingHTTPSConnection('foo')
	>>> c._compare_hostname('foo')
	>>> c.hostname_matches_cert

	# Still too short
	>>> c = ValidatingHTTPSConnection('foo.')
	>>> c._compare_hostname('foo.')
	>>> c.hostname_matches_cert

	'''

	connect_parts = reversed([ part for part in self.host.lower().split('.') if part ])
	cert_parts = reversed([ part for part in host.lower().split('.') if part ])
	if len(cert_parts) <= 1:
	    _log.debug('ValidatingHTTPSConnection hostname %r is too short', host)
	    return

	if len(connect_parts) != len(cert_parts):
	    _log.debug('ValidatingHTTPSConnection hostname %r != %r (len)', self.host, host)
	    return

	for p1, p2 in zip(connect_parts, cert_parts):
	    if p1 != p2 and p2 != '*':
		_log.debug('ValidatingHTTPSConnection hostname %r != %r', self.host, host)
		return

	_log.debug('ValidatingHTTPSConnection hostname %r == %r', self.host, host)
	self.hostname_matches_cert = True

    def connect(self):
	msg = 'getaddrinfo returns an empty list'
	for af, socktype, proto, canonname, addr in getaddrinfo(self.host,
	    self.port, 0, SOCK_STREAM):

	    try:
		_log.debug('ValidatingHTTPSConnection to %r', addr)
		ssl = SSLSocket(socket(af, socktype, proto),
		    keyfile=self.key_file, certfile=self.cert_file,
		    cert_reqs=self.cert_reqs, ca_certs=self.ca_certs,
		    ssl_version=self.ssl_version)
		ssl.connect(addr)

	    except SocketError, e:
		_log.info('ValidatingHTTPSConnection to %r: %s', addr, e)
		msg = e
		self.sock = None
		continue

	    server_attrs = ssl.getpeercert()
	    # getpeercert() returns {} if the certificate was not verified, in
	    # which case it doesn't matter what the name in the certificate is.
	    if self.check_hostname and server_attrs:
		self.hostname_matches_cert = False
		names = []

		for gntype, gn in server_attrs.get('subjectAltName', ()):
		    if gntype == 'DNS':
			self._compare_hostname(gn)
			names.append(gn)

		    else:
			_log.warn('ValidatingHTTPSConnection unhandled subjectAltName type: %s=%r', gntype, gn)

		# Only look at attributes in the first rdn.
		for attr,val in server_attrs['subject'][0]:
		    if attr == 'commonName':
			self._cmp_hostname(val)
			names.append(val)

		if not self.hostname_matches_cert:
		    raise CertNameMismatchError(self.host, names)

	    # Newer ssl object implements makefile, fileno, etc.  No need to
	    # use FakeSocket wrapper
	    self.sock = ssl
	    break

	if not self.sock:
	    raise SocketError, msg

    class HTTPSHandler(object):
	_value = None

	def make_https_open(self, cls):
	    def https_open(self, req):
		return self.do_open(cls, req)
	    return https_open

	def __get__(self, x, cls):
	    if self._value:
		return self._value

	    name = cls.__name__
	    if name.endswith('Connection'):
		name = name[:-len('Connection')]
	    name += 'Handler'
	    doc = 'Variant of urllib2.HTTPSHandler which uses %s' % cls.__name__

	    self._value = new.classobj(name, (urllib2.HTTPSHandler,),
		dict(https_open=self.make_https_open(cls), __doc__=doc))
	    return self._value
    HTTPSHandler = HTTPSHandler()



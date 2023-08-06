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

'''Provides an interface to CAS servers and services'''

from urlparse import urlparse, urlunparse, urljoin
from urllib import urlencode

import urllib2
from urllib2 import URLError, HTTPCookieProcessor

from copy import copy

import posixpath

import logging

# Try to use lxml.etree for it's HTMLParser
try:
    import lxml.etree as ET

except ImportError:
    import xml.etree.cElementTree as ET


__all__ = ['CASServer', 'CASService', 'InvalidTicketError', 'login_to_cas_service']

_log = logging.getLogger(__name__)


class InvalidTicketError(ValueError):
    def __init__(self, ticket):
	message = 'CAS got an INVALID TICKET %r' % ticket
	super(InvalidTicketError, self).__init__(message)
	self.ticket = ticket


class CASServer(object):
    '''Handle representing a CAS server

    '''

    def __init__(self, baseurl, opener=None):
	'''Construct a CASServer object.

	Arguments:
	    baseurl	The URL of the CAS server (e.g. http://cas.example.org/cas/)
	    opener	Optional urllib2 opener.  Allows to have a validated connection to the server.
	'''

	self.baseurl = baseurl
	self.urlopen = opener and opener.open or urllib2.urlopen

    def __repr__(self):
	return '<%s object for %s>' % (self.__class__.__name__, self.baseurl)

    def login(self, service, renew=False, gateway=None):
	'''Generate a URL to log into a CASService.

	>>> srv = CASServer('https://cas.example.org/cas')
	>>> svc = type('CASService', (object,), dict(url='https://www.example.org/blah/login'))()
	>>> srv.login(svc)
	'https://cas.example.org/cas/login?service=https%3A%2F%2Fwww.example.org%2Fblah%2Flogin'

	>>> srv.login(svc, gateway=True)
	'https://cas.example.org/cas/login?gateway=true&service=https%3A%2F%2Fwww.example.org%2Fblah%2Flogin'

	>>> srv.login(svc, renew=True)
	'https://cas.example.org/cas/login?renew=true&service=https%3A%2F%2Fwww.example.org%2Fblah%2Flogin'

	>>> srv.login(svc, gateway=True, renew=True)
	AssertionError: Cannot use renew and gateway together

	'''

	scheme, host, path, search, query, fragment = urlparse(self.baseurl)
	path = posixpath.join(path, 'login')
	query = dict(service=service.url)
	assert not (renew and gateway), 'Cannot use renew and gateway together'
	if renew:
	    query.update(renew='true')
	elif gateway is True:
	    query.update(gateway='true')
	url = urlunparse((scheme, host, path, search, urlencode(query), fragment))

	return url

    def validate(self, service, ticket, renew=False):
	'''Check with the CAS server to see if a service ticket is valid.

	Arguments:
	    service	The CASService being logged into.  This should match
			the service the ticket was generated for.
	    ticket	The ticket being validated.
	    renew	Option to assert that the user's identity was
			revalidated for this ticket.

	Returns the username associated with the ticket, raises
	InvalidTicketError if the ticket is not valid.

	Be aware that CAS service tickets are not reusable.  This prevents
	replay attacks.
	'''

	scheme, host, path, search, query, fragment = urlparse(self.baseurl)
	path = posixpath.join(path, 'validate')
	query = dict(service=service.url, ticket=ticket)
	if renew:
	    query.update(renew='true')
	url = urlunparse((scheme, host, path, search, urlencode(query), fragment))

	_log.info('CASServer.validate validating ticket %r for service %r', ticket, service.url)
	
	try:
	    vf = self.urlopen(url)

	except URLError, e:
	    _log.warning('CASServer.validate unable to contact %r: %s', url, e)
	    raise

	resp = vf.readline().rstrip('\n')
	if resp == 'yes':
	    username = vf.readline().rstrip('\n')
	    _log.info('CASServer.validate validated ticket %r was valid; username=%r', ticket, username)
	    return username

	_log.warning('CASServer.validate validation failed for ticket %r; resp=%r', ticket, resp)

	# I don't think this should ever happen, but maybe I'll find out if it does!
	assert resp=='no'

	raise InvalidTicketError(ticket)

    # Even if we don't implement the proxy bits, this provides an error channel
    # which is potentially useful (in the unlikely event of an error)
    # def serviceValidate(self, service, ticket, renew=False, pgt_url=None):
    #     pass


class CASService(object):
    '''Handle representing a CAS service'''

    def __init__(self, url):
	'''Construct a CASService object.

	Arguments:
	    url		The url of the service.
	'''
	self.url = url

    def base(self, url):
	'''Create a new CASService relocated to be under a different host+scheme+path

	>>> svc = CASService('http://www.example.com/login')
	>>> svc.url
	'http://www.example.com/login'

	>>> svc.base('http://www.example.com/test').url
	'http://www.example.com/test/login'
	
	'''
	svc = copy(self)
	scheme, host, base_path = urlparse(url)[0:3]
	path, search, query, frag = urlparse(self.url)[2:]
	svc.url = urlunparse((scheme, host, posixpath.join(base_path, path[1:]), search, query, frag))
	return svc

    def __repr__(self):
	return '<%s object for %s>' % ( self.__class__.__name__, self.url )


def login_to_cas_service(url, username, password, opener=None):
    '''Attempt to authenticate to a CAS /login form using the provided username and password.
    
    username and password may be callables
    
    On success returns a file handle for the log in page and a urllib2 opener that contains a cookiejar.

    On failure....something else will happen.
    '''

    if not opener:
	opener = urllib2.build_opener()

    if not any( isinstance(h, HTTPCookieProcessor) for h in opener.handlers ):
	opener.add_handler(HTTPCookieProcessor())

    # cookiejar = ( h for h in opener.handlers if isinstance(h, HTTPCookieProcessor) ).next().cookiejar

    login_fh = opener.open(url)
    login_str = login_fh.read()

    try:
	# HTMLParser comes from lxml
	login_doc = ET.fromstring(login_str, parser=ET.HTMLParser(), base_url=login_fh.url)

    except (AttributeError, SyntaxError):
	# This part may need to be tweaked, my use requires a recovering parser, so I haven't tested this
	login_doc = ET.fromstring(login_str)

    action,params = _get_login_bits(login_doc, login_fh.url)

    params.append(('username', username() if callable(username) else username))
    params.append(('password', password() if callable(password) else password))
    data = urlencode(params, True)

    # If successful, this should redirect to the service which will validate
    # the service ticket and create a session (or something)
    logged_in_fh = opener.open(action, data)

    #return logged_in_fh.url,cookiejar
    return logged_in_fh, opener


def _get_login_bits(doc, base):

    class XMLNS(object):
	'''Utility class to generate xml names using clark notation'''

	def __init__(self, ns=None):
	    self.ns = ns

	def __getitem__(self, attr, default=None):
	    if self.ns:
		return '{%s}%s' % (self.ns, attr)
	    return attr

	def __getattribute__(self, attr):
	    try:
		return object.__getattribute__(self, attr)

	    except AttributeError:
		return self[attr]

    xhtml = XMLNS('http://www.w3.org/1999/xhtml')
    html = XMLNS()

    searchall = lambda el, tag: el.findall('.//'+html[tag])+el.findall('.//'+xhtml[tag])

    cas_login_form_inputs = set(('lt', 'username', 'password'))

    for form in searchall(doc, 'form'):
	action = urljoin(base, form.get('action'))
	inputs = searchall(form, 'input')
	if cas_login_form_inputs & set( el.get('name') for el in inputs ) == cas_login_form_inputs:
	    # Strip out the username and password elements because we are providing them
	    params = [ (el.get('name'),el.get('value', '')) for el in inputs
		if el.get('name') not in ('username', 'password', None) ]
	    return action,params
	    

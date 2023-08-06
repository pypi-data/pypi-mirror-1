#     Copyright (C) 2009
#     Associated Universities, Inc.  Washington DC, USA.
#
#     Copying and distribution of this file, with or without modification,
#     are permitted in any medium without royalty provided the copyright
#     notice and this notice are preserved.  This file is offered as-is,
#     without any warranty.

'''Test authentication against a CAS server using cas_dance.py

This is NOT an automated test.
'''

import sys

import logging

from urlparse import urlunparse
from urllib import urlencode
import urllib2

import wsgiref.simple_server
from cgi import FieldStorage

from caslib.cas_dance import *
from caslib.validating_https import *


logging.basicConfig()
logging.root.level = logging.DEBUG


CAS_SERVER = sys.argv[1]


username = None

def handle_validation(environ, start_response):
    global username
    store = FieldStorage(fp=environ['wsgi.input'], environ=environ)
    ticket = store.getvalue('ticket')
    if ticket:
	print 'Got ticket: %r' % ticket

    else:
	start_response('200 What?', [('Content-type', 'text-plain')])
	yield "Whatchya doin'?\n"
	return

    try:
	username = cas_server.validate(cas_service, ticket)
	print 'Welcome, %r.' % username
	start_response('200 Alright', [('Content-type', 'text/plain')])
	yield 'Welcome, %r.\n' % username

    except InvalidTicketError, e:
	print e
	start_response("401 You ain't him!", [('Content-type', 'text/plain')])
	yield '%s\n\n' % e
	yield 'Get outta here you weasly rascal!\n'

    except urllib2.URLError, e:
	print e
	start_response('401 Sorry', [('Content-type', 'text/plain')])
	yield '%s\n\n' % e
	yield "It's not your fault, but you still can't come in.\n"

class ConfiguredValidatingHTTPSConnection(ValidatingHTTPSConnection):
    ca_certs = '/etc/pki/tls/certs/ca-bundle.crt'

opener = urllib2.build_opener(ConfiguredValidatingHTTPSConnection.HTTPSHandler)

http_server = wsgiref.simple_server.make_server('localhost', 0, handle_validation)
http_server_address = urlunparse(('http', '%s:%u' % ( http_server.server_name, http_server.server_port ), '', '', '', ''))

cas_server = CASServer(CAS_SERVER, opener=opener)
cas_service = CASService(http_server_address)

print 'Log in here:'
print '  %s' % cas_server.login(cas_service)

try:
    while not username:
	http_server.handle_request()

except KeyboardInterrupt:
    print
    print 'Well, OK.  Then just, uh, just nevermind.'


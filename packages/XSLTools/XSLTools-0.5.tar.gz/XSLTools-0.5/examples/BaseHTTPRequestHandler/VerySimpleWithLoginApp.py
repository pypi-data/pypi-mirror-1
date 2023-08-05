#!/usr/bin/env python

from WebStack.Adapters.BaseHTTPRequestHandler import deploy
import VerySimpleWithLogin

# Get a simple Web site.

host = "" # or an absolute URL (without path)
resource = VerySimpleWithLogin.get_site(host)

# Special magic incantation.

print "Serving..."
deploy(resource, handle_errors=0)

# vim: tabstop=4 expandtab shiftwidth=4

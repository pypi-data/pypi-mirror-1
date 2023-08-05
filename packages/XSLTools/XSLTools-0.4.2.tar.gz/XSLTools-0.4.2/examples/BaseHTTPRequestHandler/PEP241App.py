#!/usr/bin/env python

from WebStack.Adapters.BaseHTTPRequestHandler import deploy
import PEP241

# Get a simple Web site.

resource = PEP241.get_site()

# Special magic incantation.

print "Serving..."
deploy(resource, handle_errors=0)

# vim: tabstop=4 expandtab shiftwidth=4

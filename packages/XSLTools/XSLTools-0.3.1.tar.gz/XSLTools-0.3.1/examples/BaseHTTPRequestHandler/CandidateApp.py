#!/usr/bin/env python

from WebStack.Adapters.BaseHTTPRequestHandler import deploy
import Candidate

# Get a simple Web site.

resource = Candidate.get_site()

# Special magic incantation.

print "Serving..."
deploy(resource, handle_errors=0)

# vim: tabstop=4 expandtab shiftwidth=4

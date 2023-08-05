#!/usr/bin/env python

from WebStack.Adapters.BaseHTTPRequestHandler import deploy
import Candidate

# Get a simple Web site.
# NOTE: Change the filesystem encoding if appropriate.

resource = Candidate.get_site("iso-8859-15")

# Special magic incantation.

print "Serving..."
deploy(resource, handle_errors=0)

# vim: tabstop=4 expandtab shiftwidth=4

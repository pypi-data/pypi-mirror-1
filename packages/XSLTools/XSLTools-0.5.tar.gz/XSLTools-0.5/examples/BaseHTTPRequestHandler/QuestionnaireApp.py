#!/usr/bin/env python

from WebStack.Adapters.BaseHTTPRequestHandler import deploy
import Questionnaire

# Get a simple Web site.

resource = Questionnaire.get_site()

# Special magic incantation.

print "Serving..."
deploy(resource, handle_errors=0)

# vim: tabstop=4 expandtab shiftwidth=4

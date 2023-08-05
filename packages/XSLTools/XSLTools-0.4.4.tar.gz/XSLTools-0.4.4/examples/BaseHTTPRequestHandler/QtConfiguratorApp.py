#!/usr/bin/env python

from WebStack.Adapters.BaseHTTPRequestHandler import deploy
import QtConfigurator

# Get a simple Web site.

resource = QtConfigurator.get_resource("PyQtWeb")

# Special magic incantation.

print "Serving..."
deploy(resource, handle_errors=0)

# vim: tabstop=4 expandtab shiftwidth=4

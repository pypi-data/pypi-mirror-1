#!/usr/bin/env python

from WebStack.Adapters.Twisted import deploy
import VerySimple

# Get a simple Web site.

resource = VerySimple.get_site()

# Special magic incantation.

print "Serving..."
deploy(resource, handle_errors=0)

# vim: tabstop=4 expandtab shiftwidth=4

#!/usr/bin/env python

from WebStack.Adapters.BaseHTTPRequestHandler import deploy
import Dictionary
from Dictionary.Dict import Dict

# Initialise a dictionary.

import sys
if len(sys.argv) < 2:
    print "Please specify a file to be indexed."
    sys.exit(1)

filename = sys.argv[1]

if len(sys.argv) > 2:
    encoding = sys.argv[2]
else:
    encoding = None

dict = Dict(filename, encoding)

# Get a simple Web site.

resource = Dictionary.get_site(dict)

# Special magic incantation.

print "Serving..."
deploy(resource, handle_errors=0)

# vim: tabstop=4 expandtab shiftwidth=4

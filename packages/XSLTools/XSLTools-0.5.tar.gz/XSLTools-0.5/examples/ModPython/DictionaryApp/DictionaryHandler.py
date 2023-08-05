#!/usr/bin/env python

# Initialise paths and the dictionary.
# NOTE: Path manipulation requires manual customisation.

import sys
#sys.path.append("/home/paulb/Software/Python/WebStack")
#sys.path.append("/home/paulb/Software/Python/XSLTools")
#sys.path.append("/home/paulb/Software/Python/XSLTools/examples/Common")
#sys.path.append("/home/paulb/Software/Python/libxml2dom")
#filename = "/home/paulb/Software/Python/XSLTools/docs/LICENCE.txt"
filename = "/usr/share/doc/python2.4-xsltools/docs/gpl-3.0.txt"
encoding = None

from WebStack.Adapters import ModPython
import Dictionary
from Dictionary.Dict import Dict

dict = Dict(filename, encoding)

# Get a simple Web site.

resource = Dictionary.get_site(dict)

# NOTE: Not sure if the resource should be maintained in a resource pool.

def handler(req):
    global resource
    return ModPython.respond(req, resource, handle_errors=0)

# vim: tabstop=4 expandtab shiftwidth=4

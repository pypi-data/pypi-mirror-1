#!/usr/bin/env python

# NOTE: Path manipulation requires manual customisation.

import sys
sys.path.append("/home/paulb/Software/Python/WebStack")
sys.path.append("/home/paulb/Software/Python/XSLTools")
sys.path.append("/home/paulb/Software/Python/XSLTools/examples/Common")
sys.path.append("/home/paulb/Software/Python/libxml2dom")

from WebStack.Adapters import ModPython
import Candidate

# Get a simple Web site.
# NOTE: Change the filesystem encoding if appropriate.

resource = Candidate.get_site("iso-8859-15")

# NOTE: Not sure if the resource should be maintained in a resource pool.

def handler(req):
    global resource
    return ModPython.respond(req, resource, handle_errors=0)

# vim: tabstop=4 expandtab shiftwidth=4

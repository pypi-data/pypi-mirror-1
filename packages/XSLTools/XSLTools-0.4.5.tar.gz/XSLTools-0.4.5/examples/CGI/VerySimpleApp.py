#!/usr/bin/env python

# NOTE: Path manipulation requires manual customisation.

import sys
sys.path.append("/home/paulb/Software/Python/WebStack")
sys.path.append("/home/paulb/Software/Python/XSLTools")
sys.path.append("/home/paulb/Software/Python/XSLTools/examples/Common")
sys.path.append("/home/paulb/Software/Python/libxml2dom")

from WebStack.Adapters.CGI import deploy
import VerySimple

# Get a simple Web site.

resource = VerySimple.get_site()

# Special magic incantation.

deploy(resource, handle_errors=0)

# vim: tabstop=4 expandtab shiftwidth=4

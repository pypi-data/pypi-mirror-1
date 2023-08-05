#!/usr/bin/env python

# Initialise paths and the dictionary.
# NOTE: Path manipulation requires manual customisation.

import sys
#sys.path.append("/home/paulb/Software/Python/WebStack")
#sys.path.append("/home/paulb/Software/Python/XSLTools")
#sys.path.append("/home/paulb/Software/Python/XSLTools/examples/Common")
#sys.path.append("/home/paulb/Software/Python/libxml2dom")
#filename = "/home/paulb/Software/Python/XSLTools/docs/LICENCE.txt"
filename = "/usr/share/doc/python2.4-xsltools/docs/LICENCE.txt"
encoding = None

from WebStack.Adapters.CGI import deploy
import Dictionary
from Dictionary.Dict import Dict

dict = Dict(filename, encoding)

# Get a simple Web site.

resource = Dictionary.get_site(dict)

# Special magic incantation.

deploy(resource, handle_errors=0)

# vim: tabstop=4 expandtab shiftwidth=4

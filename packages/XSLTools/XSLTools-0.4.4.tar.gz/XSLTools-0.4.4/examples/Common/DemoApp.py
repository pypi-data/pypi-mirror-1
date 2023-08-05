#!/usr/bin/env python

"""
A demonstration of XSLTools. This is a quick and dirty combination of an
adapter, employing lots of resources, and the index page resource.
"""

# Import the things which publish parts of the application.

from WebStack.Resources.ResourceMap import MapResource
import os, sys

# Here are all the example applications.

import Candidate
import Configurator
import Dictionary
from Dictionary.Dict import Dict
import Questionnaire
import PEP241
import Recursive
import VerySimple

# A very simple index page.

from WebStack.Generic import ContentType

# Configuration settings.
# NOTE: Change the filesystem encoding if appropriate.

fsencoding = "iso-8859-15"

# Resource classes.

class DemoResource:
    def respond(self, trans):
        trans.set_content_type(ContentType("text/html"))
        trans.get_response_stream().write("""
<html>
  <head>
    <title>XSLTools Examples</title>
  </head>
  <body>
    <h1>XSLTools Examples</h1>
    <p>Here are some of the examples supplied with XSLTools:</p>
    <ul>
      <li><a href="candidate">A job candidate profile editor</a></li>
      <li><a href="configurator">A Webshop-style system configurator</a></li>
      <li><a href="dictionary">A simple word lookup interface</a></li>
      <li><a href="questionnaire">A questionnaire generator</a></li>
      <li><a href="pep241">A Python package repository user interface</a></li>
      <li><a href="recursive">A recursive template example</a></li>
      <li><a href="verysimple">A very simple example</a></li>
    </ul>
    <p>You can run all of the examples independently, too. See the
       <code>examples</code> directory for the code.</p>
  </body>
</html>""")
        trans.set_response_code(200)

# Find out where our example document will be for the dictionary example.

def get_site():

    "Define the resource mapping."

    # Find a file for use with the Dictionary example.

    exec_dir = os.path.split(sys.argv[0])[0]
    parts = os.path.split(exec_dir)
    if parts[-1] == "tools":
        parts = parts[:-1]
    parts += ("docs", "LICENCE.txt")
    doc = os.path.join(*parts)
    dict = Dict(doc)

    # Define the site resource itself.

    resource = MapResource({

        # Use the current working directory so that the installed package can still run
        # the demo.

        "candidate" : Candidate.get_site(fsencoding, use_cwd=1),
        "configurator" : Configurator.get_site(),
        "dictionary" : Dictionary.get_site(dict),
        "questionnaire" : Questionnaire.get_site(),
        "pep241" : PEP241.get_site(),
        "recursive" : Recursive.get_site(),
        "verysimple" : VerySimple.get_site(),
        "" : DemoResource(),
        })

    return resource

# Resource preparation ahead of time - useful for making installations.

def prepare_resources():
    for module in [Candidate, Configurator, Dictionary, Questionnaire, PEP241, Recursive, VerySimple]:
        module.prepare_resources()

# vim: tabstop=4 expandtab shiftwidth=4

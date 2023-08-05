#!/usr/bin/env python

"""
A demonstration of XSLTools. This is a quick and dirty combination of an
adapter, employing lots of resources, and the index page resource.
"""

# Import the things which publish parts of the application.

from WebStack.Resources.ResourceMap import MapResource
import os

# Here are all the example applications.

import Candidate
import Configurator
import Dictionary
from Dictionary.Dict import Dict
import Questionnaire
import PEP241
import VerySimple

# A very simple index page.

from WebStack.Generic import ContentType

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

    cwd = os.getcwd()
    parts = os.path.split(cwd)
    if parts[-1] == "tools":
        parts = parts[:-1]
    parts += ("docs", "LICENCE.txt")
    doc = os.path.join(*parts)
    dict = Dict(doc)

    resource = MapResource({
        "candidate" : Candidate.get_site(),
        "configurator" : Configurator.get_site(),
        "dictionary" : Dictionary.get_site(dict),
        "questionnaire" : Questionnaire.get_site(),
        "pep241" : PEP241.get_site(),
        "verysimple" : VerySimple.get_site(),
        "" : DemoResource(),
        })

    return resource

# vim: tabstop=4 expandtab shiftwidth=4

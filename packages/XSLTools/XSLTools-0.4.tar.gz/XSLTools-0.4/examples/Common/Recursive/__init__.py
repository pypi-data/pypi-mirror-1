#!/usr/bin/env python

"An example of recursive templates."

import WebStack.Generic
import XSLForms.Resources.WebResources
import XSLForms.Utils
import os

# Resource classes.

class RecursiveResource(XSLForms.Resources.WebResources.XSLFormsResource):

    "A resource providing a recursive hierarchy of editable fields."

    resource_dir = os.path.join(os.path.split(__file__)[0], "Resources")
    encoding = "utf-8"
    template_resources = {
        "recursive" : ("recursive_template.xhtml", "recursive_output.xsl")
        }
    init_resources = {
        "recursive" : ("recursive_template.xhtml", "recursive_input.xsl")
        }

    def respond_to_form(self, trans, form):

        """
        Respond to a request having the given transaction 'trans' and the given
        'form' information.
        """

        parameters = form.get_parameters()
        documents = form.get_documents()

        # Ensure the presence of a document.

        if documents.has_key("recursive"):
            recursive = documents["recursive"]
        else:
            recursive = form.new_instance("recursive")

        # Add and remove elements according to the selectors found.

        selectors = form.get_selectors()
        XSLForms.Utils.remove_elements(selectors.get("remove"))
        XSLForms.Utils.add_elements(selectors.get("add-list"), "list")
        XSLForms.Utils.add_elements(selectors.get("add-item"), "item")

        # Initialise the document, adding enumerations/ranges.

        init_xsl = self.prepare_initialiser("recursive")
        recursive = self.get_result([init_xsl], recursive)
        #print recursive.toString("iso-8859-1")

        # Start the response.

        trans.set_content_type(WebStack.Generic.ContentType("application/xhtml+xml", self.encoding))

        # Ensure that an output stylesheet exists.

        trans_xsl = self.prepare_output("recursive")
        stylesheet_parameters = {}

        # Complete the response.

        self.send_output(trans, [trans_xsl], recursive, stylesheet_parameters)

# Site map initialisation.

def get_site():

    "Return a simple Web site resource."

    # Get the main resource and the directory used by the application.

    return RecursiveResource()

# Resource preparation ahead of time - useful for making installations.

def prepare_resources():
    for cls in [RecursiveResource]:
        XSLForms.Resources.WebResources.prepare_resources(cls)

# vim: tabstop=4 expandtab shiftwidth=4

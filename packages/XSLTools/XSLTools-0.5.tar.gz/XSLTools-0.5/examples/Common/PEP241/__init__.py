#!/usr/bin/env python

"A WebStack application for a PEP 241 repository."

import WebStack.Generic
import XSLForms.Resources.WebResources
import XSLForms.Utils
import os

# Site map imports.

from WebStack.Resources.ResourceMap import MapResource
from WebStack.Resources.Selectors import EncodingSelector
from WebStack.Resources.Static import DirectoryResource

# Configuration setting.

encoding = "utf-8"

# Resource classes.

class PEP241Resource(XSLForms.Resources.WebResources.XSLFormsResource):

    "A resource providing repository browsing."

    resource_dir = os.path.join(os.path.split(__file__)[0], "Resources")
    template_resources = {
        "pep241" : ("pep241_template.xhtml", "pep241_output.xsl")
        }
    init_resources = {
        "pep241" : ("pep241_template.xhtml", "pep241_input.xsl")
        }
    document_resources = {
        "categories" : "pep241_categories.xml"
        }
    in_page_resources = {
        "platforms" : ("pep241", "pep241_output_platforms.xsl", "platforms"),
        "supported-platforms" : ("pep241", "pep241_output_supported_platforms.xsl", "supported-platforms"),
        "keywords" : ("pep241", "pep241_output_keywords.xsl", "keywords"),
        "authors" : ("pep241", "pep241_output_authors.xsl", "authors"),
        "dependencies" : ("pep241", "pep241_output_dependencies.xsl", "dependencies")
        }

    def respond_to_form(self, trans, form):

        """
        Respond to a request having the given transaction 'trans' and the given
        'form' information.
        """

        in_page_resource = self.get_in_page_resource(trans)
        parameters = form.get_parameters()
        documents = form.get_documents()
        selectors = form.get_selectors()

        # Ensure the presence of a document.

        if documents.has_key("package"):
            package = documents["package"]
        else:
            package = form.new_instance("package")

        # Add and remove elements according to the selectors found.

        XSLForms.Utils.add_elements(selectors.get("add_platform"), "platform", "platforms")
        XSLForms.Utils.remove_elements(selectors.get("remove_platform"))
        XSLForms.Utils.add_elements(selectors.get("add_supported_platform"), "supported-platform", "supported-platforms")
        XSLForms.Utils.remove_elements(selectors.get("remove_supported_platform"))
        XSLForms.Utils.add_elements(selectors.get("add_keyword"), "keyword", "keywords")
        XSLForms.Utils.remove_elements(selectors.get("remove_keyword"))
        XSLForms.Utils.add_elements(selectors.get("add_author"), "author", "authors")
        XSLForms.Utils.remove_elements(selectors.get("remove_author"))
        XSLForms.Utils.add_elements(selectors.get("add_dependency"), "dependency", "dependencies")
        XSLForms.Utils.remove_elements(selectors.get("remove_dependency"))

        # Send a response according to certain parameters.
        # When exported, an XML version of the data is returned.

        if parameters.has_key("export"):
            trans.set_content_type(WebStack.Generic.ContentType("text/xml", encoding))
            package.toStream(trans.get_response_stream(), trans.get_response_stream_encoding())

        # When not exported, the data is transformed to produce a normal Web
        # page.

        else:

            # Transform, adding enumerations/ranges.

            input_xsl = self.prepare_initialiser("pep241")
            categories_xml = self.prepare_document("categories")
            package = self.get_result([input_xsl], package, references={"category" : categories_xml})

            # Start the response.

            trans.set_content_type(WebStack.Generic.ContentType("application/xhtml+xml", encoding))

            # Ensure that an output stylesheet exists.

            if in_page_resource in self.in_page_resources.keys():
                trans_xsl = self.prepare_fragment(in_page_resource)
                stylesheet_parameters = self.prepare_parameters(parameters)
            else:
                trans_xsl = self.prepare_output("pep241")
                stylesheet_parameters = {}

            # Complete the response.

            self.send_output(trans, [trans_xsl], package, stylesheet_parameters)

            #from XSLTools import XSLOutput
            #import sys
            #proc = XSLOutput.Processor([trans_xsl], parameters=stylesheet_parameters)
            #proc.send_output(sys.stderr, "iso-8859-1", package)

# Site map initialisation.

def get_site():

    "Return a simple Web site resource."

    # Get the main resource and the directory used by the application.

    pep241_resource = PEP241Resource()
    directory = pep241_resource.resource_dir

    # Make a simple Web site.

    resource = MapResource({
        # Static resources:
        "styles" : DirectoryResource(os.path.join(directory, "styles"), {"css" : "text/css"}),
        "scripts" : DirectoryResource(os.path.join(directory, "scripts"), {"js" : "text/javascript"}),
        # In-page resources:
        "platforms" : pep241_resource,
        "supported-platforms" : pep241_resource,
        "keywords" : pep241_resource,
        "authors" : pep241_resource,
        "dependencies" : pep241_resource,
        # Main page:
        "" : pep241_resource
        })

    return EncodingSelector(resource, encoding)

# Resource preparation ahead of time - useful for making installations.

def prepare_resources():
    for cls in [PEP241Resource]:
        XSLForms.Resources.WebResources.prepare_resources(cls)

# vim: tabstop=4 expandtab shiftwidth=4

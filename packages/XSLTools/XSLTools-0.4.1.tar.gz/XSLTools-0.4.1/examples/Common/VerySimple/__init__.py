#!/usr/bin/env python

"A very simple example application."

import WebStack.Generic
import XSLForms.Resources.WebResources
import XSLForms.Utils
import os

# Site map imports.

from WebStack.Resources.ResourceMap import MapResource
from WebStack.Resources.Static import DirectoryResource

# Resource classes.

class VerySimpleResource(XSLForms.Resources.WebResources.XSLFormsResource):

    "A very simple resource providing a hierarchy of editable fields."

    resource_dir = os.path.join(os.path.split(__file__)[0], "Resources")
    encoding = "utf-8"
    template_resources = {
        #"structure" : ("structure_template.xhtml", "structure_output.xsl")
        #"structure" : ("structure_multivalue_template.xhtml", "structure_output.xsl")
        "structure" : ("structure_multivalue_label_template.xhtml", "structure_output.xsl")
        }
    init_resources = {
        #"structure" : ("structure_template.xhtml", "structure_input.xsl")
        #"structure" : ("structure_multivalue_template.xhtml", "structure_input.xsl")
        "structure" : ("structure_multivalue_label_template.xhtml", "structure_input.xsl")
        }
    transform_resources = {
        "comments" : ["structure_comments.xsl"]
        }
    document_resources = {
        #"types" : "structure_types.xml"
        "types" : "structure_types_label.xml",
        "translations" : "translations.xml"
        }
    in_page_resources = {
        "comments" : ("structure", "structure_output_comments.xsl", "comment-node")
        }

    def respond_to_form(self, trans, form):

        """
        Respond to a request having the given transaction 'trans' and the given
        'form' information.
        """

        in_page_resource = self.get_in_page_resource(trans)
        parameters = form.get_parameters()
        documents = form.get_documents()

        # Ensure the presence of a document.

        if documents.has_key("structure"):
            structure = documents["structure"]
        else:
            structure = form.new_instance("structure")

        # Add and remove elements according to the selectors found.

        selectors = form.get_selectors()
        XSLForms.Utils.remove_elements(selectors.get("remove2"))
        XSLForms.Utils.add_elements(selectors.get("add2"), "subitem")
        XSLForms.Utils.remove_elements(selectors.get("remove"))
        XSLForms.Utils.add_elements(selectors.get("add"), "item")

        # Initialise the document, adding enumerations/ranges.

        structure_xsl = self.prepare_initialiser("structure")
        types_xml = self.prepare_document("types")
        structure = self.get_result([structure_xsl], structure, references={"type" : types_xml})

        # Add the comments.

        comments_xsl_list = self.prepare_transform("comments")
        structure = self.get_result(comments_xsl_list, structure)

        # Start the response.

        trans.set_content_type(WebStack.Generic.ContentType("application/xhtml+xml", self.encoding))

        # Ensure that an output stylesheet exists.

        if in_page_resource in self.in_page_resources.keys():
            trans_xsl = self.prepare_fragment(in_page_resource)
            stylesheet_parameters = self.prepare_parameters(parameters)
        else:
            trans_xsl = self.prepare_output("structure")
            stylesheet_parameters = {}

        # Complete the response.

        try:
            stylesheet_parameters["locale"] = trans.get_content_languages()[0]
        except IndexError:
            pass
        self.send_output(trans, [trans_xsl], structure, stylesheet_parameters,
            references={"translations" : self.prepare_document("translations")})

# Site map initialisation.

def get_site():

    "Return a simple Web site resource."

    # Get the main resource and the directory used by the application.

    very_simple_resource = VerySimpleResource()
    directory = very_simple_resource.resource_dir

    # Make a simple Web site.

    resource = MapResource({
        # Static resources:
        "scripts" : DirectoryResource(os.path.join(directory, "scripts"), {"js" : "text/javascript"}),
        # Main page and in-page resources:
        None : very_simple_resource
        })

    return resource

# Resource preparation ahead of time - useful for making installations.

def prepare_resources():
    for cls in [VerySimpleResource]:
        XSLForms.Resources.WebResources.prepare_resources(cls)

# vim: tabstop=4 expandtab shiftwidth=4

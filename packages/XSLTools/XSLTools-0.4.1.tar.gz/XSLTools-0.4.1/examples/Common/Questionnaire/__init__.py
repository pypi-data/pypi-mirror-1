#!/usr/bin/env python

"A WebStack questionnaire application."

import WebStack.Generic
import XSLForms.Resources.WebResources
import XSLForms.Utils
import os

# Site map imports.

from WebStack.Resources.ResourceMap import MapResource
from WebStack.Resources.Static import DirectoryResource

# Resource classes.

class QuestionnaireEditorResource(XSLForms.Resources.WebResources.XSLFormsResource):

    "A resource providing a questionnaire editor."

    resource_dir = os.path.join(os.path.split(__file__)[0], "Resources")
    encoding = "utf-8"
    template_resources = {
        "question" : ("question_template.xhtml", "question_output.xsl")
        }

    def respond_to_form(self, trans, form):

        """
        Respond to a request having the given transaction 'trans' and the given
        'form' information.
        """

        parameters = form.get_parameters()
        documents = form.get_documents()
        selectors = form.get_selectors()

        # Ensure the presence of a document.

        if documents.has_key("questionnaire"):
            questionnaire = documents["questionnaire"]
        else:
            questionnaire = form.new_instance("questionnaire")

        # Add and remove elements according to the selectors found.

        XSLForms.Utils.remove_elements(selectors.get("remove-question"))
        XSLForms.Utils.add_elements(selectors.get("add-choice"), "choice")
        XSLForms.Utils.remove_elements(selectors.get("remove-choice"))

        # Add questions using the normal request parameter.

        if parameters.has_key("add-question"):
            new_question = questionnaire.ownerDocument.createElementNS(None, "question")
            questionnaire.xpath("questionnaire")[0].appendChild(new_question)

        # Send a response according to certain parameters.
        # When exported, an XML version of the data is returned.

        if parameters.has_key("export"):
            trans.set_content_type(WebStack.Generic.ContentType("text/xml", self.encoding))
            questionnaire.toStream(trans.get_response_stream(), trans.get_response_stream_encoding())

        # When not exported, the data is transformed to produce a normal Web
        # page.

        else:

            # Start the response.

            trans.set_content_type(WebStack.Generic.ContentType("application/xhtml+xml", self.encoding))

            # Ensure that an output stylesheet exists.

            trans_xsl = self.prepare_output("question")

            # Complete the response.

            self.send_output(trans, [trans_xsl], questionnaire)

# Site map initialisation.

def get_site():

    "Return a simple Web site resource."

    # Get the main resource and the directory used by the application.

    questionnaire_resource = QuestionnaireEditorResource()
    directory = questionnaire_resource.resource_dir

    # Make a simple Web site.

    resource = MapResource({
        # Static resources:
        "styles" : DirectoryResource(os.path.join(directory, "styles"), {"css" : "text/css"}),
        # Main page:
        "" : questionnaire_resource
        })

    return resource

# Resource preparation ahead of time - useful for making installations.

def prepare_resources():
    for cls in [QuestionnaireEditorResource]:
        XSLForms.Resources.WebResources.prepare_resources(cls)

# vim: tabstop=4 expandtab shiftwidth=4

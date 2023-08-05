#!/usr/bin/env python

"A dictionary example application."

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

class DictionaryResource(XSLForms.Resources.WebResources.XSLFormsResource):

    "A simple resource providing dictionary lookup."

    resource_dir = os.path.join(os.path.split(__file__)[0], "Resources")
    template_resources = {
        "words" : ("words_template.xhtml", "words_output.xsl")
        }
    in_page_resources = {
        "matches" : ("words", "words_output_entry.xsl", "matches-node"),
        #"word" : ("words", "words_output_word.xsl", "word-node")
        }

    def __init__(self, dict):

        "Initialise the resource with the given 'dict'."

        self.dict = dict

    def respond_to_form(self, trans, form):

        """
        Respond to a request having the given transaction 'trans' and the given
        'form' information.
        """

        in_page_resource = self.get_in_page_resource(trans)
        parameters = form.get_parameters()
        documents = form.get_documents()

        # Ensure the presence of a document.

        if documents.has_key("words"):
            words = documents["words"]
        else:
            words = form.new_instance("words")

        # Add and remove elements according to the selectors found.

        selectors = form.get_selectors()
        XSLForms.Utils.remove_elements(selectors.get("remove"))
        XSLForms.Utils.add_elements(selectors.get("add"), "entry")

        # Ensure all entries have a matches element.
        # Ensure all matches elements have at least one choice.
        # Copy selected matches to their corresponding text field.

        all_entries = words.xpath("words/entry")

        for entry in all_entries:
            matches_list = entry.xpath("matches")
            if len(matches_list) == 0:
                matches = words.createElement("matches")
                entry.appendChild(matches)
            else:
                matches = matches_list[0]

            if len(entry.xpath("matches/match-enum")) == 0:
                match_enum = words.createElement("match-enum")
                match_enum.setAttribute("word", "")
                matches.appendChild(match_enum)

        # Find requested search locations.

        if selectors.has_key("search"):
            entries = selectors["search"]
        elif in_page_resource == "matches":
            entries = all_entries
        else:
            entries = []

        # Transform, adding dictionary information.

        for entry in entries:
            word = entry.getAttribute("word")
            if word != "":
                matches = entry.xpath("matches")[0]
                for found_word in self.dict.find(word):
                    match_enum = words.createElement("match-enum")
                    match_enum.setAttribute("word", found_word)
                    matches.appendChild(match_enum)

        # Copy selected values into text fields.
        # NOTE: Since libxml2dom does not guarantee node equality for two nodes
        # NOTE: referring to the same thing, we cannot just loop over all the
        # NOTE: entries and query whether they reside in the search locations.

        for entry in all_entries:
            matches = entry.xpath("matches")[0]
            if matches.hasAttribute("word"):
                word = matches.getAttribute("word")
                if word != "" and word.startswith(entry.getAttribute("word")):
                    entry.setAttribute("word", word)

        # Start the response.

        trans.set_content_type(WebStack.Generic.ContentType("application/xhtml+xml", encoding))

        # Ensure that an output stylesheet exists.

        if in_page_resource in self.in_page_resources.keys():
            trans_xsl = self.prepare_fragment(in_page_resource)
            stylesheet_parameters = self.prepare_parameters(parameters)
        else:
            trans_xsl = self.prepare_output("words")
            stylesheet_parameters = {}

        # Complete the response.

        self.send_output(trans, [trans_xsl], words, stylesheet_parameters)
        #from XSLTools import XSLOutput
        #import sys
        #proc = XSLOutput.Processor([trans_xsl], parameters=stylesheet_parameters)
        #proc.send_output(sys.stderr, "iso-8859-1", words)

# Site map initialisation.

def get_site(dict):

    """
    Return a simple Web site resource using the given 'dict' - a dictionary
    employed by the application.
    """

    # Get the main resource and the directory used by the application.

    dictionary_resource = DictionaryResource(dict)
    directory = dictionary_resource.resource_dir

    # Make a simple Web site.

    resource = MapResource({
        # Static resources:
        "scripts" : DirectoryResource(os.path.join(directory, "scripts"), {"js" : "text/javascript"}),
        # Main page and in-page resources:
        "" : dictionary_resource,
        "matches" : dictionary_resource
        })

    return EncodingSelector(resource, encoding)

# Resource preparation ahead of time - useful for making installations.

def prepare_resources():
    for cls in [DictionaryResource]:
        XSLForms.Resources.WebResources.prepare_resources(cls)

# vim: tabstop=4 expandtab shiftwidth=4

#!/usr/bin/env python

"A WebStack application for a system configurator."

import WebStack.Generic
import XSLForms.Utils
import XSLForms.Resources.WebResources
import os

# Site map imports.

from WebStack.Resources.ResourceMap import MapResource
from WebStack.Resources.Selectors import EncodingSelector
from WebStack.Resources.Static import DirectoryResource

# Configuration settings.

encoding = "utf-8"

# Resource classes.

class ConfiguratorResource(XSLForms.Resources.WebResources.XSLFormsResource):

    "A resource providing a system configurator."

    resource_dir = os.path.join(os.path.split(__file__)[0], "Resources")
    template_resources = {
        "configuration" : ("config_template.xhtml", "config_output.xsl")
        }
    init_resources = {
        "configuration" : ("config_template.xhtml", "config_input.xsl")
        }
    transform_resources = {
        "filter" : ["config_filter.xsl"]
        }
    document_resources = {
        "accessories" : "config_accessories.xml",
        "base-system" : "config_base_system.xml",
        "cpu" : "config_cpu.xml",
        "hard-disk" : "config_hard_disk.xml",
        "keyboard" : "config_keyboard.xml",
        "memory-unit" : "config_memory_unit.xml",
        "mouse" : "config_mouse.xml",
        "screen" : "config_screen.xml",
        "storage-unit" : "config_storage_unit.xml",
        "translations" : "translations.xml"
        }
    in_page_resources = {
        "cpu" : ("configuration", "config_output_cpu.xsl", "cpu-node"),
        "memory" : ("configuration", "config_output_memory.xsl", "memory-node"),
        "hard-disks" : ("configuration", "config_output_harddisks.xsl", "hard-disks-node"),
        "accessories" : ("configuration", "config_output_accessories.xsl", "accessories-node")
        }

    def respond_to_form(self, trans, form):

        """
        Respond to a request having the given transaction 'trans' and the given
        'form' information.
        """

        in_page_resource = self.get_in_page_resource(trans)
        parameters = form.get_parameters()
        documents = form.get_documents()

        # Creating selected elements.

        selectors = form.get_selectors(create=1)

        # Ensure the presence of a document.

        if documents.has_key("configuration"):
            configuration = documents["configuration"]
        else:
            configuration = form.new_instance("configuration")

        # Add and remove elements according to the selectors found.

        XSLForms.Utils.add_elements(selectors.get("add-memory-unit"), "memory-unit")
        XSLForms.Utils.remove_elements(selectors.get("remove-memory-unit"))
        XSLForms.Utils.add_elements(selectors.get("add-storage-unit"), "storage-unit")
        XSLForms.Utils.remove_elements(selectors.get("remove-storage-unit"))
        XSLForms.Utils.add_elements(selectors.get("add-hard-disk"), "hard-disk")
        XSLForms.Utils.remove_elements(selectors.get("remove-hard-disk"))

        # Send a response according to certain parameters.
        # When exported, an XML version of the data is returned.

        if parameters.has_key("export"):
            trans.set_content_type(WebStack.Generic.ContentType("text/xml", encoding))
            configuration.toStream(trans.get_response_stream(), trans.get_response_stream_encoding())

        # When not exported, the data is transformed to produce a normal Web
        # page.

        else:

            # Transform, adding enumerations/ranges.

            init_xsl = self.prepare_initialiser("configuration")
            configuration = self.get_result([init_xsl], configuration,
                references={
                    "accessories" : self.prepare_document("accessories"),
                    "base-system" : self.prepare_document("base-system"),
                    "cpu" : self.prepare_document("cpu"),
                    "hard-disk" : self.prepare_document("hard-disk"),
                    "keyboard" : self.prepare_document("keyboard"),
                    "memory-unit" : self.prepare_document("memory-unit"),
                    "mouse" : self.prepare_document("mouse"),
                    "screen" : self.prepare_document("screen"),
                    "storage-unit" : self.prepare_document("storage-unit")
                })

            # Filter out inappropriate choices.

            filter_xsl_list = self.prepare_transform("filter")
            configuration = self.get_result(filter_xsl_list, configuration)

            # Start the response.

            trans.set_content_type(WebStack.Generic.ContentType("application/xhtml+xml", encoding))

            # Ensure that an output stylesheet exists.

            if in_page_resource in self.in_page_resources.keys():
                trans_xsl = self.prepare_fragment(in_page_resource)
                stylesheet_parameters = self.prepare_parameters(parameters)
            else:
                trans_xsl = self.prepare_output("configuration")
                stylesheet_parameters = {}

            # Complete the response.

            try:
                stylesheet_parameters["locale"] = trans.get_content_languages()[0]
            except IndexError:
                pass
            self.send_output(trans, [trans_xsl], configuration, stylesheet_parameters,
                references={"translations" : self.prepare_document("translations")})

            #from XSLTools import XSLOutput
            #import sys
            #proc = XSLOutput.Processor([trans_xsl], parameters=stylesheet_parameters,
            #    references={"translations" : self.prepare_document("translations")})
            #proc.send_output(sys.stderr, "iso-8859-1", configuration)

# Site map initialisation.

def get_site():

    "Return a simple Web site resource."

    # Get the main resource and the directory used by the application.

    configurator_resource = ConfiguratorResource()
    directory = configurator_resource.resource_dir

    # Make a simple Web site.

    resource = MapResource({
        # Static resources:
        "styles" : DirectoryResource(os.path.join(directory, "styles"), {"css" : "text/css"}),
        "scripts" : DirectoryResource(os.path.join(directory, "scripts"), {"js" : "text/javascript"}),
        # Main page:
        "" : configurator_resource,
        # Fragments:
        "cpu" : configurator_resource,
        "memory" : configurator_resource,
        "hard-disks" : configurator_resource,
        "accessories" : configurator_resource
        })

    return EncodingSelector(resource, encoding)

# Resource preparation ahead of time - useful for making installations.

def prepare_resources():
    for cls in [ConfiguratorResource]:
        XSLForms.Resources.WebResources.prepare_resources(cls)

# vim: tabstop=4 expandtab shiftwidth=4

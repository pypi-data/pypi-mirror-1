#!/usr/bin/env python

"A job candidate editing application."

import WebStack.Generic
from WebStack.Repositories.Directory import DirectoryRepository
import XSLForms.Resources.WebResources
import XSLForms.Utils
import os
import libxml2dom

# Site map imports.

from WebStack.Resources.ResourceMap import MapResource
from WebStack.Resources.Static import DirectoryResource

# Resource classes.

class AdminResource(XSLForms.Resources.WebResources.XSLFormsResource):

    "A resource providing administration facilities for job candidate profiles."

    resource_dir = os.path.join(os.path.split(__file__)[0], "Resources")
    encoding = "utf-8"
    template_resources = {
        "admin" : ("admin_template.xhtml", "admin_output.xsl")
        }
    init_resources = {
        "admin" : ("admin_template.xhtml", "admin_input.xsl")
        }

    def respond_to_form(self, trans, form):

        """
        Respond to a request having the given transaction 'trans' and the given
        'form' information.
        """

        parameters = form.get_parameters()
        documents = form.get_documents()

        # Get the "show" and "edit" resource paths.
        # NOTE: These should be obtained from the site map.

        vpath = trans.get_processed_virtual_path_info(self.path_encoding)
        show_path = trans.get_path_without_info(self.path_encoding) + trans.update_path(vpath, "show")
        edit_path = trans.get_path_without_info(self.path_encoding) + trans.update_path(vpath, "edit")

        # Ensure the presence of a document.

        form_is_new = 0
        if documents.has_key("admin"):
            admin = documents["admin"]
        else:
            admin = form.new_instance("admin")
            form_is_new = 1

        # Redirect if one of the CVs is to be shown or edited.

        selectors = form.get_selectors()
        if selectors.has_key("show"):
            name = selectors["show"][0].getAttribute("name")
            trans.redirect(trans.encode_path(show_path, self.path_encoding) +
                "?name=%s" % trans.encode_path(name, self.path_encoding))
        elif selectors.has_key("edit"):
            name = selectors["edit"][0].getAttribute("name")
            trans.redirect(trans.encode_path(edit_path, self.path_encoding) +
                "?name=%s" % trans.encode_path(name, self.path_encoding))

        # Add and remove elements according to the selectors found.

        XSLForms.Utils.remove_elements(selectors.get("remove"))
        XSLForms.Utils.add_elements(selectors.get("new"), "cv", "cvs")

        # Transform, adding enumerations/ranges.

        init_xsl = self.prepare_initialiser("admin")
        admin = self.get_result([init_xsl], admin)

        # Synchronise the repository with the CVs found.

        cvs = admin.xpath("/admin/cvs")[0]
        repository = DirectoryRepository(os.path.join(self.resource_dir, "candidates"))
        for key in repository.keys():
            if key.startswith("candidate-"):
                name = key[len("candidate-"):]
                # NOTE: Apostrophes not quoted.
                if not cvs.xpath("cv[@name = '%s']" % name):
                    if form_is_new:
                        cv = admin.createElement("cv")
                        cv.setAttribute("name", name)
                        cvs.appendChild(cv)
                    else:
                        del repository[key]

        # Start the response.

        trans.set_content_type(WebStack.Generic.ContentType("application/xhtml+xml", self.encoding))

        # Ensure that an output stylesheet exists.

        trans_xsl = self.prepare_output("admin")
        stylesheet_parameters = {}

        # Complete the response.

        self.send_output(trans, [trans_xsl], admin, stylesheet_parameters)

class DisplayResource(XSLForms.Resources.WebResources.XSLFormsResource):

    "A resource providing editing facilities for a job candidate profile."

    resource_dir = os.path.join(os.path.split(__file__)[0], "Resources")
    encoding = "utf-8"
    template_resources = {
        "candidate_display" : ("candidate_display_template.xhtml", "candidate_display_output.xsl")
        }
    init_resources = {
        "candidate" : ("candidate_template.xhtml", "candidate_input.xsl")
        }
    document_resources = {
        "status" : "candidate_status.xml"
        }

    def respond_to_form(self, trans, form):

        """
        Respond to a request having the given transaction 'trans' and the given
        'form' information.
        """

        parameters = form.get_parameters()
        documents = form.get_documents()
        fields = trans.get_fields_from_path(self.path_encoding)
        name = fields.get("name", [u"None"])[0]

        # Ensure the presence of a document.

        if documents.has_key("candidate"):
            candidate = documents["candidate"]
        else:
            repository = DirectoryRepository(os.path.join(self.resource_dir, "candidates"))
            if repository is None or not repository.has_key("candidate-%s" % name):
                candidate = form.new_instance("candidate")
            else:
                candidate = libxml2dom.parseString(repository["candidate-%s" % name])

        # Transform, adding enumerations/ranges.

        init_xsl = self.prepare_initialiser("candidate")
        status_xml = self.prepare_document("status")
        candidate = self.get_result([init_xsl], candidate, references={"status" : status_xml})

        # Start the response.

        trans.set_content_type(WebStack.Generic.ContentType("application/xhtml+xml", self.encoding))

        # Ensure that an output stylesheet exists.
        # Handle the "show" operation.

        trans_xsl = self.prepare_output("candidate_display")
        stylesheet_parameters = {}

        # Complete the response.

        self.send_output(trans, [trans_xsl], candidate, stylesheet_parameters)

class CandidateResource(XSLForms.Resources.WebResources.XSLFormsResource):

    "A resource providing editing facilities for a job candidate profile."

    resource_dir = os.path.join(os.path.split(__file__)[0], "Resources")
    encoding = "utf-8"
    template_resources = {
        "candidate" : ("candidate_template.xhtml", "candidate_output.xsl")
        }
    init_resources = {
        "candidate" : ("candidate_template.xhtml", "candidate_input.xsl")
        }
    document_resources = {
        "status" : "candidate_status.xml"
        }

    def respond_to_form(self, trans, form):

        """
        Respond to a request having the given transaction 'trans' and the given
        'form' information.
        """

        parameters = form.get_parameters()
        documents = form.get_documents()
        fields = trans.get_fields_from_path(self.path_encoding)
        name = fields.get("name", [u"None"])[0]

        # Get the "show" resource path.
        # NOTE: This should be obtained from the site map.

        vpath = trans.get_processed_virtual_path_info(self.path_encoding)
        show_path = trans.get_path_without_info(self.path_encoding) + trans.update_path(vpath, "show")
        admin_path = trans.get_path_without_info(self.path_encoding) + trans.update_path(vpath, "")

        # Ensure the presence of a document.

        if documents.has_key("candidate"):
            candidate = documents["candidate"]
        else:
            repository = DirectoryRepository(os.path.join(self.resource_dir, "candidates"))
            if repository is None or not repository.has_key("candidate-%s" % name):
                candidate = form.new_instance("candidate")
            else:
                candidate = libxml2dom.parseString(repository["candidate-%s" % name])

        # Add and remove elements according to the selectors found.

        selectors = form.get_selectors()
        XSLForms.Utils.remove_elements(selectors.get("remove"))
        XSLForms.Utils.add_elements(selectors.get("add-skill"), "skill", "skills")
        XSLForms.Utils.add_elements(selectors.get("add-qualification"), "qualification", "qualifications")
        XSLForms.Utils.add_elements(selectors.get("add-employment"), "employment", "experience")

        # Transform, adding enumerations/ranges.

        init_xsl = self.prepare_initialiser("candidate")
        status_xml = self.prepare_document("status")
        candidate = self.get_result([init_xsl], candidate, references={"status" : status_xml})

        # Redirect if the CV is to be shown.

        if parameters.has_key("show"):

            # Save the candidate information.

            repository = DirectoryRepository(os.path.join(self.resource_dir, "candidates"))
            repository["candidate-%s" % name] = candidate.toString()
            trans.redirect(trans.encode_path(show_path, self.path_encoding) +
                "?name=%s" % trans.encode_path(name, self.path_encoding))

        # Redirect if the administration interface is to be used.

        elif parameters.has_key("admin"):

            # Save the candidate information.

            repository = DirectoryRepository(os.path.join(self.resource_dir, "candidates"))
            repository["candidate-%s" % name] = candidate.toString()
            trans.redirect(trans.encode_path(admin_path, self.path_encoding))

        # Start the response.

        trans.set_content_type(WebStack.Generic.ContentType("application/xhtml+xml", self.encoding))

        # Ensure that an output stylesheet exists.

        trans_xsl = self.prepare_output("candidate")
        stylesheet_parameters = {}

        # Complete the response.

        self.send_output(trans, [trans_xsl], candidate, stylesheet_parameters)

# Site map initialisation.

def get_site():

    "Return a simple Web site resource."

    # Get the main resource and the directory used by the application.

    candidate_resource = CandidateResource()
    display_resource = DisplayResource()
    admin_resource = AdminResource()
    directory = candidate_resource.resource_dir

    # Make a simple Web site.

    resource = MapResource({
        "edit" : candidate_resource,
        "show" : display_resource,
        "" : admin_resource
        })

    return resource

# vim: tabstop=4 expandtab shiftwidth=4

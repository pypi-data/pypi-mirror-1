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
from WebStack.Resources.Selectors import EncodingSelector
from WebStack.Resources.Static import DirectoryResource

# Configuration setting.

encoding = "utf-8"

# Resource classes.

class AdminResource(XSLForms.Resources.WebResources.XSLFormsResource):

    "A resource providing administration facilities for job candidate profiles."

    resource_dir = os.path.join(os.path.split(__file__)[0], "Resources")
    template_resources = {
        "admin" : ("admin_template.xhtml", "admin_output.xsl")
        }
    init_resources = {
        "admin" : ("admin_template.xhtml", "admin_input.xsl")
        }

    def __init__(self, repository):
        self.repository = repository

    def respond_to_form(self, trans, form):

        """
        Respond to a request having the given transaction 'trans' and the given
        'form' information.
        """

        parameters = form.get_parameters()
        documents = form.get_documents()

        # Get the "show" and "edit" resource paths.
        # NOTE: These should be obtained from the site map.

        vpath = trans.get_processed_virtual_path_info()
        show_path = trans.get_path_without_info() + trans.update_path(vpath, "show")
        edit_path = trans.get_path_without_info() + trans.update_path(vpath, "edit")

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
            trans.redirect(trans.encode_path(show_path) +
                "?name=%s" % trans.encode_path(name))
        elif selectors.has_key("edit"):
            name = selectors["edit"][0].getAttribute("name")
            trans.redirect(trans.encode_path(edit_path) +
                "?name=%s" % trans.encode_path(name))

        # Add and remove elements according to the selectors found.

        XSLForms.Utils.remove_elements(selectors.get("remove"))
        XSLForms.Utils.add_elements(selectors.get("new"), "cv", "cvs")

        # Transform, adding enumerations/ranges.

        init_xsl = self.prepare_initialiser("admin")
        admin = self.get_result([init_xsl], admin)

        # Synchronise the repository with the CVs found.

        cvs = admin.xpath("/admin/cvs")[0]
        for key in self.repository.keys():
            if key.startswith("candidate-"):
                name = key[len("candidate-"):]
                # NOTE: Apostrophes not quoted.
                if not cvs.xpath("cv[@name = '%s']" % name):
                    if form_is_new:
                        cv = admin.createElement("cv")
                        cv.setAttribute("name", name)
                        cvs.appendChild(cv)
                    else:
                        del self.repository[key]

        # Start the response.

        trans.set_content_type(WebStack.Generic.ContentType("application/xhtml+xml", encoding))

        # Ensure that an output stylesheet exists.

        trans_xsl = self.prepare_output("admin")
        stylesheet_parameters = {}

        # Complete the response.

        self.send_output(trans, [trans_xsl], admin, stylesheet_parameters)

class DisplayResource(XSLForms.Resources.WebResources.XSLFormsResource):

    "A resource providing editing facilities for a job candidate profile."

    resource_dir = os.path.join(os.path.split(__file__)[0], "Resources")
    template_resources = {
        "candidate_display" : ("candidate_display_template.xhtml", "candidate_display_output.xsl")
        }
    init_resources = {
        "candidate" : ("candidate_template.xhtml", "candidate_input.xsl")
        }
    document_resources = {
        "status" : "candidate_status.xml"
        }

    def __init__(self, repository):
        self.repository = repository

    def respond_to_form(self, trans, form):

        """
        Respond to a request having the given transaction 'trans' and the given
        'form' information.
        """

        parameters = form.get_parameters()
        documents = form.get_documents()
        fields = trans.get_fields_from_path()
        name = fields.get("name", [u"None"])[0]

        # Ensure the presence of a document.

        if documents.has_key("candidate"):
            candidate = documents["candidate"]
        else:
            if self.repository is None or not self.repository.has_key("candidate-%s" % name):
                candidate = form.new_instance("candidate")
            else:
                candidate = libxml2dom.parseString(self.repository["candidate-%s" % name])

        # Transform, adding enumerations/ranges.

        init_xsl = self.prepare_initialiser("candidate")
        status_xml = self.prepare_document("status")
        candidate = self.get_result([init_xsl], candidate, references={"status" : status_xml})

        # Start the response.

        trans.set_content_type(WebStack.Generic.ContentType("application/xhtml+xml", encoding))

        # Ensure that an output stylesheet exists.
        # Handle the "show" operation.

        trans_xsl = self.prepare_output("candidate_display")
        stylesheet_parameters = {}

        # Complete the response.

        self.send_output(trans, [trans_xsl], candidate, stylesheet_parameters)

class CandidateResource(XSLForms.Resources.WebResources.XSLFormsResource):

    "A resource providing editing facilities for a job candidate profile."

    resource_dir = os.path.join(os.path.split(__file__)[0], "Resources")
    template_resources = {
        "candidate" : ("candidate_template.xhtml", "candidate_output.xsl")
        }
    init_resources = {
        "candidate" : ("candidate_template.xhtml", "candidate_input.xsl")
        }
    document_resources = {
        "status" : "candidate_status.xml"
        }

    def __init__(self, repository):
        self.repository = repository

    def respond_to_form(self, trans, form):

        """
        Respond to a request having the given transaction 'trans' and the given
        'form' information.
        """

        parameters = form.get_parameters()
        documents = form.get_documents()
        fields = trans.get_fields_from_path()
        name = fields.get("name", [u"None"])[0]

        # Get the "show" resource path.
        # NOTE: This should be obtained from the site map.

        vpath = trans.get_processed_virtual_path_info()
        show_path = trans.get_path_without_info() + trans.update_path(vpath, "show")
        admin_path = trans.get_path_without_info() + trans.update_path(vpath, "")

        # Ensure the presence of a document.

        if documents.has_key("candidate"):
            candidate = documents["candidate"]
        else:
            if self.repository is None or not self.repository.has_key("candidate-%s" % name):
                candidate = form.new_instance("candidate")
            else:
                candidate = libxml2dom.parseString(self.repository["candidate-%s" % name])

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

            self.repository["candidate-%s" % name] = candidate.toString()
            trans.redirect(trans.encode_path(show_path) +
                "?name=%s" % trans.encode_path(name))

        # Redirect if the administration interface is to be used.

        elif parameters.has_key("admin"):

            # Save the candidate information.

            self.repository["candidate-%s" % name] = candidate.toString()
            trans.redirect(trans.encode_path(admin_path))

        # Start the response.

        trans.set_content_type(WebStack.Generic.ContentType("application/xhtml+xml", encoding))

        # Ensure that an output stylesheet exists.

        trans_xsl = self.prepare_output("candidate")
        stylesheet_parameters = {}

        # Complete the response.

        self.send_output(trans, [trans_xsl], candidate, stylesheet_parameters)

# Site map initialisation.

def get_site(fsencoding=None, use_cwd=0):

    "Return a simple Web site resource."

    if use_cwd:
        resource_dir = os.getcwd()
    else:
        resource_dir = os.path.join(os.path.split(__file__)[0], "Resources")
    repository = DirectoryRepository(os.path.join(resource_dir, "candidates"), fsencoding)

    # Get the main resource and the directory used by the application.

    candidate_resource = CandidateResource(repository)
    display_resource = DisplayResource(repository)
    admin_resource = AdminResource(repository)

    # Make a simple Web site.

    resource = MapResource({
        "edit" : candidate_resource,
        "show" : display_resource,
        "" : admin_resource
        })

    return EncodingSelector(resource, encoding)

# Resource preparation ahead of time - useful for making installations.

def prepare_resources():
    for cls in [AdminResource, DisplayResource, CandidateResource]:
        XSLForms.Resources.WebResources.prepare_resources(cls)

# vim: tabstop=4 expandtab shiftwidth=4

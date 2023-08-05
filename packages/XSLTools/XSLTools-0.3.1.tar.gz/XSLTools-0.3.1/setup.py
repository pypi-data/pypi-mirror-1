#! /usr/bin/env python

from distutils.core import setup

import XSLForms

setup(
    name         = "XSLTools",
    description  = "Modules and packages for the development of XML/XSL-based applications",
    author       = "Paul Boddie",
    author_email = "paul@boddie.org.uk",
    url          = "http://www.boddie.org.uk/python/XSLTools.html",
    version      = XSLForms.__version__,
    packages     = ["XSLForms", "XSLForms.Resources", "XSLTools"],
    package_data = {"XSLForms" : ["XSL/*.xsl"]},
    scripts      = ["scripts/xslform_extract.py", "scripts/xslform_output.py",
                    "scripts/xslform_prepare.py", "scripts/xslform_preparemacro.py",
                    "scripts/xslform_input.py",
                    "scripts/xslform_qt_prepare.py", "scripts/xslform_qt_template.py",
                    "scripts/xslform_schema.py"]
    )

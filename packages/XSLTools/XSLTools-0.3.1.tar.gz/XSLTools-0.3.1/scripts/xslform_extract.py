#!/usr/bin/env python

"Prepare a templating stylesheet fragment."

import XSLForms.Prepare
import sys

if __name__ == "__main__":
    try:
        input_xml = sys.argv[1]
        output_xml = sys.argv[2]
        element_id = sys.argv[3]
    except IndexError:
        print "Please specify an output template, an output filename and an element identifier."
        print "For example:"
        print "xslform_extract.py output.xsl output_element.xsl element"
        sys.exit(1)

    XSLForms.Prepare.make_stylesheet_fragment(input_xml, output_xml, element_id)

# vim: tabstop=4 expandtab shiftwidth=4

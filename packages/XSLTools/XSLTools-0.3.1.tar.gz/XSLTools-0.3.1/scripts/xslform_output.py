#!/usr/bin/env python

"Prepare a templating stylesheet."

import XSLForms.Output
from XSLTools import XSLOutput
import libxml2dom
import sys

if __name__ == "__main__":
    try:
        input_xml = sys.argv[1]
        trans_xsl = sys.argv[2]
        output_xml = sys.argv[3]
    except IndexError:
        print "Please specify an input filename, a template filename and an output filename."
        print "For example:"
        print "xslform_output.py input.xml output.xsl output.xhtml"
        sys.exit(1)

    proc = XSLOutput.Processor([trans_xsl])
    proc.send_output(open(output_xml, "wb"), "utf-8", libxml2dom.parse(input_xml))

# vim: tabstop=4 expandtab shiftwidth=4

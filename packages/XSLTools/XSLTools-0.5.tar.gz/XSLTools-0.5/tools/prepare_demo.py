#!/usr/bin/env python

"Prepare the demonstration program's resources."

import os, sys

# Find out where the XSLTools distribution directory is.

program = sys.argv[0]
cwd = os.path.split(program)[0]
parts = os.path.split(cwd)
if parts[-1] == "tools":
    parts = parts[:-1]
base = os.path.join(*parts)

# Set up the environment and obtain the demo resource.

sys.path.insert(0, base)
sys.path.insert(0, os.path.join(base, "examples", "Common"))

import DemoApp
DemoApp.prepare_resources()

# vim: tabstop=4 expandtab shiftwidth=4

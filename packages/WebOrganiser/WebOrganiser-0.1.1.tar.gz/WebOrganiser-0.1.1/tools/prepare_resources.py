#!/usr/bin/env python

"Prepare the application resources."

import os, sys

# Find out where the package distribution directory is.

program = sys.argv[0]
cwd = os.path.split(program)[0]
parts = os.path.split(cwd)
if parts[-1] == "tools":
    parts = parts[:-1]
base = os.path.join(*parts)

# Set up the environment and obtain the application resources.

sys.path.insert(0, os.path.join(base, "applications"))

import WebCalendar
WebCalendar.prepare_resources()

# vim: tabstop=4 expandtab shiftwidth=4

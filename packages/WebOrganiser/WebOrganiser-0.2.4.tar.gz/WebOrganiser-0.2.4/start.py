#!/usr/bin/env python

"""
A simple start script which runs the BaseHTTPRequestHandler version but which
also sets up the environment first.
"""

import sys, os

# Try and find the applications.

program = os.path.abspath(sys.argv[0])
cwd = os.path.split(program)[0]

# Set up the environment and obtain the application resource.

weborganiser = os.path.join(cwd, "WebOrganiser")
if os.path.exists(weborganiser):
    sys.path.insert(0, cwd)
applications = os.path.join(cwd, "applications")
if os.path.exists(applications):
    sys.path.insert(0, applications)
server_dir = os.path.join(cwd, "servers", "BaseHTTPRequestHandler")
if os.path.exists(server_dir):
    sys.path.insert(0, server_dir)

import WebCalendarApp
sys.exit(WebCalendarApp.main(sys.argv))

# vim: tabstop=4 expandtab shiftwidth=4

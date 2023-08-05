##############################################################################
#
# Copyright (c) 2006-2007 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""zeocltl -- control a ZEO server using zdaemon.

Usage: zeocltl [options] [action [arguments]]

Options:
-h/--help -- print usage message and exit
-i/--interactive -- start an interactive shell after executing commands
action [arguments] -- see below

Actions are commands like "start", "stop" and "status". If -i is
specified or no action is specified on the command line, a "shell"
interpreting actions typed interactively is started (unless the
configuration option default_to_interactive is set to false). Use the
action "help" to find out about available actions.
"""

import os, sys
from ZEO import zeoctl

WIN32 = False
if sys.platform[:3].lower() == "win":
    WIN32 = True

# TODO: This all probably needs to be adjusted for Windows in the same way
# that plone.recipe.zope2instance is

def main(args=None):
    zeoctl.main(args)

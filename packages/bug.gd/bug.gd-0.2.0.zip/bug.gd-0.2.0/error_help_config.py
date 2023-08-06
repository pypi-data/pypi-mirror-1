#!/usr/bin/env python

import re
import os
import sys
import buggdUtil

def doCustomize():
    # 1) Ask the user for his email
    email = buggdUtil.getUserEmail()

    # 2) Get the site customize path
    filename = buggdUtil.getSiteCustomize()

    # 3) Write the lines to store the email and register error_help()
    lines = ["\n",
             "#### BEGIN ERROR_HELP SETTINGS\n",
             "import error_help\n",
             "error_help.register_builtin('"+email+"')\n",
             "#### END ERROR_HELP SETTINGS\n",
             "\n"]

    f = open(filename, 'a')
    f.writelines(lines)

    f.close()
    # 4) Done
    print """\n\n******** Setup is complete!"""
    print """Whenever you get an exception inside Python, type error_help() to search for
solutions to that error.  If you have any problems, please contact bugs@bug.gd!
            News blog: http://blog.bug.gd
********"""

# Tell the user we need to edit sitecustomize.py and will create it if it
question ="""\n\nHello! You're installing the bug.gd error network package. This tool is
designed to find workarounds to common errors, but we'll need your help
to provide advice if no one else reported the issue before you.\n\n
Setup will edit your sitecustomize.py and create it if it doesn't exist.
  Type 'YES' to enable the global error_help() command [recommended]
  Type 'NO' otherwise\n"""

def error_config():
    response = raw_input(question)

    if response.upper() == "YES":
        doCustomize()
    else:
        print "Configuration canceled."
        pass

if __name__  == '__main__':
    error_config()



#!/usr/bin/env python

from distutils.core import setup
setup(name='bug.gd',
      version='0.1.4',
      description='Get help for Python errors in your interactive console',
      author='Ted from bug.gd',
      author_email='bugs@bug.gd',
      py_modules=['buggd', 'buggdXMLRPC', 'error_help', 'buggdUtil'],
      url='http://bug.gd/download/',
     )

# Lazy copy and pasting that will some day undermine us!
# But not today because I am tired.
import re
def getUserEmail():
    """Ask the user for an email address, then return it."""
    email = None
    bNeedEmail = True
    tries = 0
    while bNeedEmail:
        # Ask for the email (I really wanted this to sound more forceful, but I hear that's bad UI)
        email = raw_input('''\nIn order to share solutions, this service requires an email
address to ask you how you solved problems. (No spam, promise.)\n
Please enter the email you wish to use for bug.gd:\n''')
        
        # Quick validate
        pattern = re.compile('[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,4}', re.I)
        m = pattern.match(email)
        if m == None:
            email = None
            tries = tries + 1
        else:
            bNeedEmail = False

        if tries == 3:
            break
        
    return email


import os
import sys

def getSiteCustomizePath():
    """Return the full path to sitecustomize.py or none if it does not exist in the python search path"""
    path = None
    try:
        mod = __import__('sitecustomize')
        path = mod.__file__
        # Split off the extension and make sure it's just .py
        temp = os.path.splitext(path)
        path = temp[0] + '.py'
    except ImportError:
        path = None
    return path

# 0) Tell the user we need to edit sitecustomize.py and will create it if it
#    Maybe move this up higher?  Question??? More like a statement.
print """\n***** bug.gd error network\n\nHello! You're installing the bug.gd error network package. This tool is
designed to find workarounds to common errors.\n"""

# 1) Ask the user for his email
email = getUserEmail()

# 2) Get the site customize path
filename = getSiteCustomizePath()
create = False
packages_path = None
if filename == None:
    create = True
    # Make the sitecustomize.py in site-packages
    paths = sys.path
    for path in paths:
        if path.find('site-packages') != -1:
            packages_path = path.split('site-packages')[0] + 'site-packages'
            filename = packages_path + 'sitecustomize.py'
            break
        
if filename == None:
    # We better do something smart I guess even though I don't think should happen
    paths = sys.path
    for path in paths:
        if path.find('Python') != -1:
            path_split = path.split('Python')
            packages_path = path_split[0] + 'Python' + path_split[1][0:2]
            filename = packages_path + 'sitecustomize.py'
            break

# 3) Write the lines to store the email and register error_help()
lines = "import error_help\nerror_help.register_builtin('"+email+"')\n"
    
# 6) Done
print """\n\n******** Setup is ALMOST complete!
******** Setup is ALMOST complete!

To invoke error_help() from within Python, manually add these lines to"""
print filename + " :\n"
print lines

raw_input("\n--> Press ENTER once you've added these lines <--")

print """
Whenever you get an exception inside Python, type error_help() to search for
solutions to that error.

If you have any problems, please contact bugs@bug.gd and let us know!
            News blog: http://blog.bug.gd
********"""


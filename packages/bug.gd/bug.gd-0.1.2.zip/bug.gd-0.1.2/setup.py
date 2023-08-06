#!/usr/bin/env python

from distutils.core import setup
setup(name='bug.gd',
      version='0.1.2',
      description='Get help for Python errors in your interactive console',
      author='Ted from bug.gd',
      author_email='bugs@bug.gd',
      py_modules=['buggd', 'buggdXMLRPC', 'error_help'],
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
        email = raw_input('''\nThe error network works only through your help. The service requires an email
address to ask you later how you solved problems. (No spam, promise.)\n
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
question ="""\n\nHello! You're installing the bug.gd error network package. This tool is
designed to find workarounds to common errors, but we'll need your help
to provide advice if no one else reported the issue before you.\n\n
Setup will edit your sitecustomize.py and create it if it doesn't exist.
  Type 'YES' to enable the global error_help() command [recommended]
  Type 'NO' otherwise\n"""
response = raw_input(question)

if response.upper() == "YES":
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
                filename = packages_path + '/sitecustomize.py'
                print filename
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

    # 3) Open sitecustomzie.py
    f = None
    if create:
        f = open(filename, 'w')
    else:
        f = open(filename, 'a')

    # 4) Write the lines to store the email and register error_help()
    lines = ["\n",
             "# The following lines were added by the bug.gd error network package\n",
             "#### BEGIN ERROR_HELP SETTINGS\n",
             "import sys\n",
             "import error_help\n",
             "setattr(sys.modules['__builtin__'], '_buggdEmail', '" + email + "')\n",
             "setattr(sys.modules['__builtin__'], 'error_help', error_help.error_help)\n",
             "#### END ERROR_HELP SETTINGS\n"]
    f.writelines(lines)

    # 5) Close
    f.close()

    # 6) Done
    print """\n\n******** SETUP COMPLETE 
To use the error network, whenever you get an exception inside Python, you can
type error_help() to search the network for that exception.
\nIf you're not getting the best results, try to update:
    easy_install -U bug.gd
This tool will be updating during beta to optimize it for Python errors.

If you have any problems, please contact bugs@bug.gd and let us know!
                News blog: http://blog.bug.gd
********"""

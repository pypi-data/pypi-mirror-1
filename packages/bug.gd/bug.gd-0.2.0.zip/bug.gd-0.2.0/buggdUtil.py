import re
import os
import distutils.sysconfig as sysconfig

def getUserEmail():
    """Ask the user for an email address, then return it."""
    email = None
    bNeedEmail = True
    tries = 0

    input_msg = '''\nIn order to share solutions, this service requires an email
address to ask you how you solved problems. (No spam, promise.)\n
Please enter the email you wish to use for bug.gd:\n'''
    
    while bNeedEmail:
        # Ask for the email
        email = raw_input(input_msg)

        input_msg = '''Our bad validator didn't like your email address.\n
Please enter the email you wish to use for bug.gd:\n'''
        
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

def getSiteCustomize():
    """Return the full path to sitecustomize.py, even if it's not there?!"""
    path = None
    try:
        mod = __import__('sitecustomize')
        path = mod.__file__
        # Split off the extension and make sure it's just .py
        temp = os.path.splitext(path)
        path = temp[0] + '.py'
    except ImportError:
        path = sysconfig.get_python_lib()
        path = os.path.join(path, 'sitecustomize.py')
    return path

import re

def getUserEmail():
    """Ask the user for an email address, then return it."""
    email = None
    bNeedEmail = True
    tries = 0
    while bNeedEmail:
        # Ask for the email
        email = raw_input('Please enter the email you wish to use for bug.gd:\n')
        
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

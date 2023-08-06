import sys
import buggd

import buggdUtil

email = None

# Not sure about these being global right now
_buggd = None
_search_id = None
_error_list = None

def register_builtin(email_address="anonymousPYTHON@bug.gd"):
    ''' Adds error_help() to builtins '''
    global email
    email = str(email_address)
    setattr(sys.modules['__builtin__'], 'error_help', error_help)
    
def error_search(error_text):
    global _buggd
    global _search_id
    global _error_list
    _search_id = _buggd.submitError(email, error_text)

    _error_list = _buggd.doSearch(_search_id)

    # Print the top 5 errors
    for i in range(0, 5):
        e = _buggd.getErrorInfo(_error_list[i])
        print_error(i + 1, len(_error_list), e)    

def print_error(list_number, list_length, error):
    print '========== ' + str(list_number) + ' of ' + str(list_length) + ' =========='        
    print 'Error: ' + error.error
    print 'Solution: ' + error.solution    

def error_help(item_number = None):
    """Search for the error stored in sys.last_value on bug.gd"""
    global _buggd
    global _search_id
    global _error_list
    global email
    
    # Init buggd
    if _buggd == None:
        _buggd = buggd.buggd()
        
    # Check Email
    if email == None:
        # Ask for user email
        email = buggdUtil.getUserEmail()
        
    # Different parameters
    if item_number != None:
        if type(item_number) == str:
            error_search(item_number)
        else:
            if type(item_number) == int:    
                if _error_list != None:
                #Lookup and print the error_info
                    e = _buggd.getErrorInfo(_error_list[item_number - 1])
                    print_error(item_number, len(_error_list), e)
                else:
                    print "No error cached yet.  Type 'error_help()' to lookup the last error."
    else:
        if sys.__dict__.has_key("last_value"):
            # Do search on bug (TO DO: Add in the trace. [import traceback])
            # Fields I'll want -> filename.py, 
            error_search(str(sys.last_value))
        else:
            # No error to lookup
            print "There was no error in sys.last_value to lookup."
            freeform_error = raw_input("Please enter some text to search for (return to cancel):\n")
            if len(freeform_error) > 0:
                error_search(freeform_error)
            


    

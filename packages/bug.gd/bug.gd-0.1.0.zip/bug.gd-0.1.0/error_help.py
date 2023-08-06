import sys
import buggd

# Not sure about these being global right now
_buggd = None
_search_id = None
_error_list = None
_buggdEmail = None

def error_help(item_number = None):
    """Search for the error stored in sys.last_value on bug.gd"""
    global _buggd
    global _search_id
    global _error_list
    global _buggdEmail
    if item_number != None:
        #Lookup and print the error_info
        e = _buggd.getErrorInfo(_error_list[item_number - 1])
        print 'Error: ' + e.error
        print 'Solution: ' + e.solution
    else:
        # Init buggd
        if _buggd == None:
            _buggd = buggd.buggd()
        # Check Email
        if _buggdEmail == None:
            # Ask for user email
            # XXXXXXXXXXXXXXXXXXXXXXXXXXXX FIX THIS XXXXXXXXXXXXXXXX
            _buggdEmail = "anonymousPYTHON@bug.gd"
        if sys.__dict__.has_key("last_value"):
            # Do search on bug (TO DO: Add in the trace. [import traceback])
            # Fields I'll want -> filename.py, 
            _search_id = _buggd.submitError(_buggdEmail, str(sys.last_value))

            _error_list = _buggd.doSearch(_search_id)

            # Print the top 5 errors
            for i in range(0, 5):
                e = _buggd.getErrorInfo(_error_list[i])
                print '========== ' + str(i + 1) + ' of ' + str(len(_error_list)) + ' =========='
                print 'Error: ' + e.error
                print 'Solution: ' + e.solution                
        else:
            # No error to lookup
            print "There was no error in sys.last_value to lookup."


    

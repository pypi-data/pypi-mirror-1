#
# File    : buggd.py
# Author  : ted shroyer
# Company : Miracle Labs
# Project : bug.gd
# Date    : March 10, 2008
#
# Description:  Provide interface to buggd api, but with nicer typing
#

import buggdXMLRPC

class buggdInvalidErrorID(Exception):
    """"""
    pass

class buggdError:
    """A bug.gd error wrapper class populated from the web api."""

    def __init__(self, error_id):
        self.error_id = error_id

        # We'll get these in a minute
        self.error = ""
        self.solution = ""

        # Just strings for now
        self.error_date = ""
        self.solution_date = ""

    def __str__(self):
        result = "ID: " + str(self.error_id) + "\n"
        result = result + "Error Date: " + str(self.error_date) + "\n"
        result = result + "Error Text: " + str(self.error) + "\n"
        result = result + "Solution Date: " + str(self.solution_date) + "\n"
        result = result + "Solution: " + str(self.solution) + "\n"
        return result


class buggd:
    """Wrapper class on top of XML-RPC"""

    def __init__(self):
        self.rpc = buggdXMLRPC.buggdXMLRPC()

    def submitError(self, email, error_text):
        """Given an email address and error_text, returns the search_id to lookup errors"""
        search_id = self.rpc.submitError(email, error_text)
        return search_id

    def doSearch(self, search_id):
        """Given a search_id from a submitted error, return a list of hits"""
        hits_dictionaries = self.rpc.doSearch(search_id)
        hits_list = []
        for hit in hits_dictionaries:
            hits_list.append(hit['error_id'])
        return hits_list

    def getErrorInfo(self, error_id):
        """Given an error_id, return the error info"""
        error = buggdError(error_id)
        error_dictionaries = self.rpc.getErrorInfo(error.error_id)
        if len(error_dictionaries) == 1:
            error_dictionary = error_dictionaries[0]
            error.error = error_dictionary['error']
            error.solution = error_dictionary['solution']
            error.error_date = error_dictionary['error_date']
            error.solution_date = error_dictionary['solution_date']
            return error
        else:
            raise buggdInvalidErrorID()

    # XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
    # TO DO?
    # Comments
    # - Don't want to get them for each error, but it would be nice if
    #   there were a comment count field in the error info so I could
    #   know if I should even bother.
    # XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX

def test():
    b = buggd()
    # XXXXXXXXXX replace with a test email id 
    search_id = b.submitError("tedshroyer@yahoo.com", "Error Text")
    errors = b.doSearch(search_id)
    for error_id in errors:
        error = b.getErrorInfo(error_id)
        print str(error)
        
if __name__ == '__main__':
    test()

    
        

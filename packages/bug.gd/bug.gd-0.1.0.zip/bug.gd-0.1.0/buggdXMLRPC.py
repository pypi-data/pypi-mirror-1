#
# File    : buggdXMLRPC.py
# Author  : ted shroyer
# Company : Miracle Labs
# Project : bug.gd
# Date    : March 5, 2008
#
# Description:  Provide a simple interface to bug.gd that wraps the bug.gd xml-
#               rpc api. 
#

import xmlrpclib

apikey = 99990

class buggdXMLRPC:
    "The buggd xml-rpc wrapper class.  The available buggd xml-rpc commands are encampsulated here."

    def __init__(self):
        self.url = 'http://soon.bug.gd/api'
        self.server = xmlrpclib.Server(self.url)

    def getUserID(self, email, reserved = apikey):
        return self.server.getUserID(reserved, email)

    def getErrorInfo(self, error_id, reserved = apikey):
        return self.server.getErrorInfo(reserved, error_id)

    def getErrorComments(self, error_id, reserved = apikey):
        return self.server.getErrorComments(reserved, error_id)

    def doSearch(self, search_id, reserved = apikey):
        return self.server.doSearch(reserved, search_id)

    def submitError(self, email, error_text, reserved = apikey):
        return self.server.submitError(reserved, email, error_text)

    def changeURL(self, url):
        self.url = url
        self.server = smlrpclib.Server(self.url)

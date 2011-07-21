import logging
import time

from twisted.internet import reactor, defer
from twisted.web.resource import Resource, NoResource
from twisted.web.server import NOT_DONE_YET
from twisted.python import log,failure
from twisted.python.log import PythonLoggingObserver
from twisted.web.template import Element, flattenString, XMLString, renderer 

class UIResource(Resource):
    isLeaf=True
    def __init__(self):
        Resource.__init__(self)
        
    
    def render_GET(self, request):
        """ GET handler"""
        log.msg("Using default GET handler", logLevel=logging.CRITICAL)
        flattenString(request, Hello()).addCallback(request.write) 
        request.finish() 
        return NOT_DONE_YET
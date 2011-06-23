import json
import logging
import time

from twisted.internet import reactor, defer
from twisted.web.resource import Resource, NoResource
from twisted.web.server import NOT_DONE_YET
from twisted.python import log,failure
from twisted.python.log import PythonLoggingObserver

from doboz_web.core.server.rest.request_parser import RequestParser
from doboz_web.core.server.rest.response_generator import ResponseGenerator
from doboz_web.core.server.rest.exception_converter import ExceptionConverter

class DefaultRestHandler(Resource):
    isLeaf=False
    def __init__(self,rootUri="http://localhost",exceptionConverter=None):
        Resource.__init__(self)
        self.logger=log.PythonLoggingObserver("dobozweb.core.server.rest.defaultresthandler")
        self.exceptionConverter=exceptionConverter or ExceptionConverter()
        self.rootUri=rootUri
        """
        what kind of content types are supported
        """
        self.valid_contentTypes=[]
        """
        what kind of query params does the Get method accept
        """
        self.validGetParams=[]        
    
    def render_GET(self, request):
        """Default GET handler"""
        log.msg("Using default GET handler", logLevel=logging.CRITICAL)
        r=ResponseGenerator(request,exceptionConverter=self.exceptionConverter,status=501)
        r._build_response("")
        return NOT_DONE_YET
    
    def render_POST(self,request):
        """Default POST handler"""
        log.msg("Using default POST handler", logLevel=logging.CRITICAL)
        r=ResponseGenerator(request,exceptionConverter=self.exceptionConverter,status=501)
        r._build_response("")
        return NOT_DONE_YET
    
    def render_PUT(self,request):
        """Default PUT handler"""
        log.msg("Using default PUT handler", logLevel=logging.CRITICAL)
        r=ResponseGenerator(request,exceptionConverter=self.exceptionConverter,status=501)
        r._build_response("")
        return NOT_DONE_YET
    
    def render_DELETE(self,request):
        """Default DELETE handler"""
        log.msg("Using default DELETE handler", logLevel=logging.CRITICAL)
        r=ResponseGenerator(request,exceptionConverter=self.exceptionConverter,status=501)
        r._build_response("")
        return NOT_DONE_YET
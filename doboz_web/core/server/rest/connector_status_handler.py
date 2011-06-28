import logging
from twisted.internet import reactor, defer
from twisted.web.resource import Resource,NoResource
from twisted.web import resource, http
from twisted.python import log,failure
from twisted.python.log import PythonLoggingObserver
from twisted.web.server import NOT_DONE_YET
from twisted.internet.task import deferLater
from doboz_web.core.server.rest.default_rest_handler import DefaultRestHandler
from doboz_web.core.server.rest.request_parser import RequestParser
from doboz_web.core.server.rest.response_generator import ResponseGenerator



class ConnectorStatusHandler(DefaultRestHandler):
    isLeaf=True
    def __init__(self,rootUri="http://localhost",exceptionConverter=None,environmentManager=None,envId=None,nodeId=None):
        DefaultRestHandler.__init__(self,rootUri,exceptionConverter)
        self.logger=log.PythonLoggingObserver("dobozweb.core.server.rest.connectorStatusHandler")
        self.environmentManager=environmentManager
        self.envId=envId   
        self.nodeId=nodeId
        self.valid_contentTypes.append("application/pollapli.connector.status+json")   
    
    
    def render_POST(self,request):
        """
        Handler for POST requests of connector status
        """
        @defer.inlineCallbacks
        def extract_args(result):  
            if result["connected"]:
                defer.returnValue((yield self.environmentManager.get_environment(self.envId).get_node(self.nodeId).connect()))
            else:
                defer.returnValue((yield self.environmentManager.get_environment(self.envId).get_node(self.nodeId).disconnect()))

        r=ResponseGenerator(request,exceptionConverter=self.exceptionConverter,status=200,contentType="application/pollapli.connector.status+json",resource="connector")
        d=RequestParser(request,"connector status",self.valid_contentTypes,self.validGetParams).ValidateAndParseParams()    
        d.addCallbacks(extract_args,errback=r._build_response)    
        d.addBoth(r._build_response)
        return NOT_DONE_YET
   
    
    def render_GET(self, request):
        """
        Handler for GET requests of connector status
        """
        def extract_args(result):
            print(self.environmentManager.get_environment(self.envId).get_node(self.nodeId).get_connector())            

            return(self.environmentManager.get_environment(self.envId).get_node(self.nodeId).get_connector())            
        r=ResponseGenerator(request,exceptionConverter=self.exceptionConverter,status=200,contentType="application/pollapli.connector.status+json",resource="connector")
        d=RequestParser(request,"connector status",self.valid_contentTypes,self.validGetParams).ValidateAndParseParams()
        d.addCallbacks(extract_args,errback=r._build_response)
        d.addBoth(r._build_response)     
        return NOT_DONE_YET
  
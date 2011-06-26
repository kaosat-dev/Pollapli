"""
.. py:module:: environments_handler
   :synopsis: rest handler for environments interaction.
"""
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
from doboz_web.core.server.rest.exception_converter import ExceptionConverter
from doboz_web.core.server.rest.node_handler import NodeHandler

class NodesHandler(DefaultRestHandler):
    """
    Resource in charge of handling the environments (plural) so :
    Adding a new environment
    Listing all environments
    """
    isLeaf=False
    def __init__(self,rootUri="http://localhost",exceptionConverter=None,environmentManager=None,envId=None):
        DefaultRestHandler.__init__(self,rootUri,exceptionConverter)
        self.logger=log.PythonLoggingObserver("dobozweb.core.server.rest.nodesHandler")
        self.environmentManager=environmentManager
        
        self.envId=envId
        self.valid_contentTypes.append("application/pollapli.nodeList+json")   
        self.validGetParams.append('id')
        self.validGetParams.append('type')
      
    def getChild(self, id, request):
        try:
            return NodeHandler(self.rootUri,self.exceptionConverter,self.environmentManager,self.envId,int(id))  
        except ValueError :
             return self#no id , so return self
    
    def render_POST(self,request):  
        """
        Handler for POST requests of nodes
        extract the data from the request body to add a new node
        """ 
        @defer.inlineCallbacks
        def extract_args(result):
            name=result["name"] or ""
            description=result.get("description") or ""
            type=result.get("type") 
            defer.returnValue((yield self.environmentManager.get_environment(self.envId).add_node(name=name,description=description,type=type)))
             
        r=ResponseGenerator(request,exceptionConverter=self.exceptionConverter,status=201,contentType="application/pollapli.node+json",resource="node")
        d=RequestParser(request,"node",self.valid_contentTypes,self.validGetParams).ValidateAndParseParams()    
        d.addCallbacks(extract_args,errback=r._build_response)    
        d.addBoth(r._build_response)
        return NOT_DONE_YET
    
    def render_GET(self, request):
        """
        Handler for GET requests of nodes
        """
        r=ResponseGenerator(request,exceptionConverter=self.exceptionConverter,status=200,contentType="application/pollapli.nodeList+json",resource="nodes")
        d=RequestParser(request,"node",self.valid_contentTypes,self.validGetParams).ValidateAndParseParams()
        d.addCallbacks(self.environmentManager.get_environment(self.envId).get_nodes,errback=r._build_response)
        d.addBoth(r._build_response)
        return NOT_DONE_YET
    
    def render_DELETE(self,request):
        """ 
        Handler for DELETE requests of nodes
        WARNING !! needs to be used very carefully, with confirmation on the client side, as it deletes ALL
        nodes
        """
        r=ResponseGenerator(request,exceptionConverter=self.exceptionConverter,status=200)
        d= self.environmentManager.get_environment(self.envId).clear_nodes()
        d.addBoth(r._build_response)
        return NOT_DONE_YET   
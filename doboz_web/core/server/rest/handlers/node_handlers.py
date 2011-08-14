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

from doboz_web.core.server.rest.handlers.default_rest_handler import DefaultRestHandler
from doboz_web.core.server.rest.request_parser import RequestParser
from doboz_web.core.server.rest.response_generator import ResponseGenerator
from doboz_web.core.server.rest.handlers.driver_handlers import DriverHandler

class NodesHandler(DefaultRestHandler):
    """
    Resource in charge of handling the nodes (plural) so :
    Adding a new node
    Listing all nodes
    etc
    """
    isLeaf=False
    def __init__(self,rootUri="",environmentManager=None,envId=None):
        DefaultRestHandler.__init__(self,rootUri)
        self.environmentManager=environmentManager
        
        self.envId=envId
        self.valid_contentTypes.append("application/pollapli.nodeList+json")   
        self.validGetParams.append('id')
        self.validGetParams.append('type')

      
    def getChild(self, id, request):
        try:
            return NodeHandler(self.rootUri+"/"+str(id),self.environmentManager,self.envId,int(id))  
        except ValueError :
             return self#no id , so return self
    
    def render_POST(self,request):  
        """
        Handler for POST requests of nodes
        extract the data from the request body to add a new node
        """ 
        r=ResponseGenerator(request,status=201,contentType="application/pollapli.node+json",resource="node",rootUri=self.rootUri)
        d=RequestParser(request,"node",self.valid_contentTypes,self.validGetParams).ValidateAndParseParams()    
        d.addCallbacks(callback=lambda params:self.environmentManager.get_environment(self.envId).add_node(**params),errback=r._build_response)    
        d.addBoth(r._build_response)
        request._call=reactor.callLater(0,d.callback,None)
        return NOT_DONE_YET
    
    def render_GET(self, request):
        """
        Handler for GET requests of nodes
        """
        r=ResponseGenerator(request,status=200,contentType="application/pollapli.nodeList+json",resource="nodes",rootUri=self.rootUri)
        d=RequestParser(request,"node",self.valid_contentTypes,self.validGetParams).ValidateAndParseParams()      
        d.addCallbacks(callback=lambda params:self.environmentManager.get_environment(self.envId).get_nodes(params),errback=r._build_response)
        d.addBoth(r._build_response)
        request._call=reactor.callLater(0,d.callback,None)
        return NOT_DONE_YET
   
             
    def render_DELETE(self,request):
        """ 
        Handler for DELETE requests of nodes
        WARNING !! needs to be used very carefully, with confirmation on the client side, as it deletes ALL
        nodes
        """
        r=ResponseGenerator(request,status=200,rootUri=self.rootUri)
        d= self.environmentManager.get_environment(self.envId).clear_nodes()
        d.addBoth(r._build_response)
        request._call=reactor.callLater(0,d.callback,None)
        return NOT_DONE_YET 
    
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""  
Single node rest handler
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
class NodeHandler(DefaultRestHandler):
    isLeaf=False
    def __init__(self,rootUri="",environmentManager=None,envId=None,nodeId=None):
        DefaultRestHandler.__init__(self,rootUri)
        self.logger=log.PythonLoggingObserver("dobozweb.core.server.rest.nodeHandler")
        self.environmentManager=environmentManager
        self.envId=envId   
        self.nodeId=nodeId
        self.valid_contentTypes.append("application/pollapli.node+json")   
        subPath=self.rootUri+"/driver"
        self.putChild("driver",DriverHandler(subPath,self.environmentManager,self.envId,self.nodeId)  
)
       
    def render_GET(self, request):
        """
        Handler for GET requests of node
        """   
        r=ResponseGenerator(request,status=200,contentType="application/pollapli.node+json",resource="node",rootUri=self.rootUri)
        d=RequestParser(request,"node",self.valid_contentTypes,self.validGetParams).ValidateAndParseParams()
        d.addCallbacks(lambda params:self.environmentManager.get_environment(self.envId).get_node(self.nodeId),errback=r._build_response)
        d.addBoth(r._build_response)     
        request._call=reactor.callLater(0,d.callback,None)
        return NOT_DONE_YET
  
    def render_PUT(self,request):
        """
        Handler for PUT requests of node
        """
        r=ResponseGenerator(request,status=200,contentType="application/pollapli.node+json",resource="node",rootUri=self.rootUri)
        d=RequestParser(request,"node",self.valid_contentTypes,self.validGetParams).ValidateAndParseParams()    
        d.addCallbacks(callback=lambda params:self.environmentManager.get_environment(self.envId).update_node(id=self.nodeId,**params),errback=r._build_response)     
        d.addBoth(r._build_response)
        request._call=reactor.callLater(0,d.callback,None)
        return NOT_DONE_YET
            
    def render_DELETE(self,request):
        """ 
        Handler for DELETE requests for the current node
        WARNING !! needs to be used very carefully, with confirmation on the client side, as it deletes the
        current node completely
        """
        r=ResponseGenerator(request,status=200,rootUri=self.rootUri) 
        d=RequestParser(request,"node",self.valid_contentTypes,self.validGetParams).ValidateAndParseParams()    
        d.addCallbacks(lambda params:self.environmentManager.get_environment(self.envId).delete_node(self.nodeId),errback=r._build_response)   
        d.addBoth(r._build_response)
        request._call=reactor.callLater(0,d.callback,None)
        return NOT_DONE_YET     
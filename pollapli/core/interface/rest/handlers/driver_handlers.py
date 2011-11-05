import logging
from twisted.internet import reactor, defer
from twisted.web.resource import Resource,NoResource
from twisted.web import resource, http
from twisted.python import log,failure
from twisted.python.log import PythonLoggingObserver
from twisted.web.server import NOT_DONE_YET
from twisted.internet.task import deferLater
from pollapli.core.interface.rest.handlers.default_rest_handler import DefaultRestHandler
from pollapli.core.interface.rest.request_parser import RequestParser
from pollapli.core.interface.rest.response_generator import ResponseGenerator
from pollapli.core.logic.components.drivers.driver import DriverManager


class DriverTypesHandler(DefaultRestHandler):
    """
    Resource in charge of handling the drivers (plural)  : WARNING !! this is a special case, as this allows acces to driver types , 
    not individual driver instances:
    Listing all driver types
    etc
    """
    isLeaf=True
    def __init__(self,rootUri=""):
        DefaultRestHandler.__init__(self,rootUri)
        self.valid_contentTypes.append("application/pollapli.driverTypeList+json")   
        self.validGetParams.append('type')

    
    def render_GET(self, request):
        """
        Handler for GET requests of driver types
        """
        r=ResponseGenerator(request,status=200,contentType="application/pollapli.driverTypeList+json",resource="driverTypes",rootUri=self.rootUri)
        d=RequestParser(request,"driverTypes",self.valid_contentTypes,self.validGetParams).ValidateAndParseParams()      
        d.addCallbacks(callback=lambda params:DriverManager.get_driverTypes(params),errback=r._build_response)
        d.addBoth(r._build_response)
        request._call=reactor.callLater(0,d.callback,None)
        return NOT_DONE_YET


class DriverHandler(DefaultRestHandler):
    isLeaf=False
    def __init__(self,rootUri="",environmentManager=None,envId=None,nodeId=None):
        DefaultRestHandler.__init__(self,rootUri)
        self.logger=log.PythonLoggingObserver("dobozweb.core.server.rest.driverHandler")
        self.environmentManager=environmentManager
        self.envId=envId   
        self.nodeId=nodeId
        self.valid_contentTypes.append("application/pollapli.driver+json")   
        subPath=self.rootUri+"/status"
        self.putChild("status",DriverStatusHandler(subPath,self.environmentManager,self.envId,self.nodeId)  
)
    
    def render_POST(self,request):
        """
        Handler for POST requests of driver
        """
        @defer.inlineCallbacks
        def extract_args(result):
           # print("in extract args",result)
            defer.returnValue((yield self.environmentManager.get_environment(self.envId).get_node(self.nodeId).set_driver(**result)))
        
        r=ResponseGenerator(request,status=201,contentType="application/pollapli.driver+json",resource="driver",rootUri=self.rootUri)
        d=RequestParser(request,"driver",self.valid_contentTypes,self.validGetParams).ValidateAndParseParams()    
        d.addCallbacks(extract_args,errback=r._build_response)    
        d.addBoth(r._build_response)
        request._call=reactor.callLater(0,d.callback,None)
        return NOT_DONE_YET
    
    def render_GET(self, request):
        """
        Handler for GET requests of driver
        """
        
        def extract_args(result):
            return(self.environmentManager.get_environment(self.envId).get_node(self.nodeId).get_driver())            
        r=ResponseGenerator(request,contentType="application/pollapli.driver+json",resource="driver",rootUri=self.rootUri)
        d=RequestParser(request,"driver",self.valid_contentTypes,self.validGetParams).ValidateAndParseParams()
        d.addCallbacks(extract_args,errback=r._build_response)
        d.addBoth(r._build_response)   
        request._call=reactor.callLater(0,d.callback,None)  
        return NOT_DONE_YET
  
    def render_PUT(self,request):
        """
        Handler for PUT requests for the driver 
        """
        @defer.inlineCallbacks
        def extract_args(result):
            name=result["name"] or ""
            description=result.get("description") or ""
            id=self.connectorId
            defer.returnValue((yield self.environmentManager.get_environment(self.envId).update_node(id=id,name=name,description=description)))
        
        r=ResponseGenerator(request,status=200,contentType="application/pollapli.driver+json",resource="driver",rootUri=self.rootUri)
        d=RequestParser(request,"driver",self.valid_contentTypes,self.validGetParams).ValidateAndParseParams()    
        d.addCallbacks(extract_args,errback=r._build_response)    
        d.addBoth(r._build_response)
        request._call=reactor.callLater(0,d.callback,None)
        return NOT_DONE_YET
            
    def render_DELETE(self,request):
        """ 
        Handler for DELETE requests for the driver
        WARNING !! needs to be used very carefully, with confirmation on the client side, as it disconnects and
        removes the driver completely
        """
        r=ResponseGenerator(request,status=200,rootUri=self.rootUri)
        d=self.environmentManager.get_environment(self.envId).get_node(self.nodeId).delete_driver()
        d.addBoth(r._build_response)
        request._call=reactor.callLater(0,d.callback,None)
        return NOT_DONE_YET   

"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""  
Connector status rest handler
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""

class DriverStatusHandler(DefaultRestHandler):
    isLeaf=True
    def __init__(self,rootUri="http://localhost",environmentManager=None,envId=None,nodeId=None):
        DefaultRestHandler.__init__(self,rootUri)
        self.logger=log.PythonLoggingObserver("dobozweb.core.server.rest.driverStatusHandler")
        self.environmentManager=environmentManager
        self.envId=envId   
        self.nodeId=nodeId
        self.valid_contentTypes.append("application/pollapli.driver.status+json")   
    
    
    def render_POST(self,request):
        """
        Handler for POST requests of connector status
        """
        @defer.inlineCallbacks
        def extract_args(result):  
            if result["connected"]:
                mode=result.get("mode") or 1
                defer.returnValue((yield self.environmentManager.get_environment(self.envId).get_node(self.nodeId).connect(mode=mode)))
            else:
                defer.returnValue((yield self.environmentManager.get_environment(self.envId).get_node(self.nodeId).disconnect()))

        r=ResponseGenerator(request,status=200,contentType="application/pollapli.driver.status+json",resource="driver status",rootUri=self.rootUri)
        d=RequestParser(request,"driver status",self.valid_contentTypes,self.validGetParams).ValidateAndParseParams()    
        d.addCallbacks(extract_args,errback=r._build_response)    
        d.addBoth(r._build_response)
        request._call=reactor.callLater(0,d.callback,None)
        return NOT_DONE_YET
   
    
    def render_GET(self, request):
        """
        Handler for GET requests of driver status
        """
        def extract_args(result):    
            return(self.environmentManager.get_environment(self.envId).get_node(self.nodeId).get_driver())            
        r=ResponseGenerator(request,contentType="application/pollapli.driver.status+json",resource="driver status",rootUri=self.rootUri)
        d=RequestParser(request,"driver status",self.valid_contentTypes,self.validGetParams).ValidateAndParseParams()
        d.addCallbacks(extract_args,errback=r._build_response)
        d.addBoth(r._build_response)   
        request._call=reactor.callLater(0,d.callback,None)  
        return NOT_DONE_YET
  
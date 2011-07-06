"""
.. py:module:: config_handler
   :synopsis: rest handler for config interaction.
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

class ConfigHandler(DefaultRestHandler):
    isLeaf=False
    def __init__(self,rootUri="http://localhost",exceptionConverter=None):
        DefaultRestHandler.__init__(self,rootUri,exceptionConverter)
        self.logger=log.PythonLoggingObserver("dobozweb.core.server.rest.environmentsHandler")
        self.valid_contentTypes.append("application/pollapli.environment+json")   
        self.putChild("nodes",NodesHandler(self.rootUri+"/environments/"+str(self.envId),self.exceptionConverter,self.environmentManager,self.envId)  
)

    
    def render_GET(self, request):
        """
        Handler for GET requests of environment
        """
        def extract_args(result):
            return(self.environmentManager.get_environment(self.envId))            
        r=ResponseGenerator(request,exceptionConverter=self.exceptionConverter,status=200,contentType="application/pollapli.environment+json",resource="environment")
        d=RequestParser(request,"environment",self.valid_contentTypes,self.validGetParams).ValidateAndParseParams()
        d.addCallbacks(extract_args,errback=r._build_response)
        d.addBoth(r._build_response)     
        return NOT_DONE_YET
  
    def render_PUT(self,request):
        """
        Handler for PUT requests of config
        """
        @defer.inlineCallbacks
        def extract_args(result):
            print("in extract args",result)
            name=result["name"] or ""
            description=result.get("description") or ""
            status=result.get("status") or "live"
            id=self.envId
            defer.returnValue((yield self.environmentManager.update_environment(id=id,name=name,description=description,status=status)))
        
        r=ResponseGenerator(request,exceptionConverter=self.exceptionConverter,status=200,contentType="application/pollapli.environment+json",resource="environment")
        d=RequestParser(request,"environment",self.valid_contentTypes,self.validGetParams).ValidateAndParseParams()    
        d.addCallbacks(extract_args,errback=r._build_response)    
        d.addBoth(r._build_response)
        return NOT_DONE_YET
            
    def render_DELETE(self,request):
        """ 
        Handler for DELETE requests of environment
        WARNING !! needs to be used very carefully, with confirmation on the client side, as it deletes the
        current environment completely
        """
        r=ResponseGenerator(request,exceptionConverter=self.exceptionConverter,status=200)
        d=self.environmentManager.remove_environment(self.envId)
        d.addBoth(r._build_response)
        return NOT_DONE_YET   
    
class AddonsHandler(DefaultRestHandler):
    isLeaf=False
    def __init__(self,rootUri="http://localhost",exceptionConverter=None):
        DefaultRestHandler.__init__(self,rootUri,exceptionConverter)
        self.logger=log.PythonLoggingObserver("dobozweb.core.server.rest.pluginsHandler")
        self.environmentManager=environmentManager
        self.envId=envId   
        self.valid_contentTypes.append("application/pollapli.addonList+json")   
        self.putChild("addons",NodesHandler(self.rootUri+"/environments/"+str(self.envId),self.exceptionConverter,self.environmentManager,self.envId)  
)

    
    def render_GET(self, request):
        """
        Handler for GET requests of addOns
        """
        r=ResponseGenerator(request,exceptionConverter=self.exceptionConverter,status=200,contentType="application/pollapli.addonList+json",resource="addOns")
        d=RequestParser(request,"addOns",self.valid_contentTypes,self.validGetParams).ValidateAndParseParams()
        d.addCallbacks(AddOnManager.get_addOns,errback=r._build_response)
        d.addBoth(r._build_response)
        return NOT_DONE_YET
  
            
    def render_DELETE(self,request):
        """ 
        Handler for DELETE requests of addOns
        WARNING !! needs to be used very carefully, with confirmation on the client side, as it deletes
        all addons completely
        """
        r=ResponseGenerator(request,exceptionConverter=self.exceptionConverter,status=200)
        d=AddOnManager.clear_addOns()
        d.addBoth(r._build_response)
        return NOT_DONE_YET   
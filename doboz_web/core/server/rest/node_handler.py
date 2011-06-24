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
from doboz_web.core.server.rest.connector_handler import ConnectorHandler
from doboz_web.core.server.rest.tasks_handler import TasksHandler

class NodeHandler(DefaultRestHandler):
    isLeaf=False
    def __init__(self,rootUri="http://localhost",exceptionConverter=None,environmentManager=None,envId=None,nodeId=None):
        DefaultRestHandler.__init__(self,rootUri,exceptionConverter)
        self.logger=log.PythonLoggingObserver("dobozweb.core.server.rest.nodeHandler")
        self.environmentManager=environmentManager
        self.envId=envId   
        self.nodeId=nodeId
        self.valid_contentTypes.append("application/pollapli.node+json")   
        subPath=self.rootUri+"/environments/"+str(self.envId)+"/nodes/"+str(self.nodeId)+"/connector"
        self.putChild("connector",ConnectorHandler(subPath,self.exceptionConverter,self.environmentManager,self.envId,self.nodeId)  
)
        subPath=self.rootUri+"/environments/"+str(self.envId)+"/nodes/"+str(self.nodeId)+"/tasks"
        self.putChild("tasks",TasksHandler(subPath,self.exceptionConverter,self.environmentManager,self.envId,self.nodeId)  
)
    
    def render_GET(self, request):
        """
        Handler for GET requests of node
        """
        def extract_args(result):
            return(self.environmentManager.get_environment(self.envId).get_node(self.nodeId))            
        r=ResponseGenerator(request,exceptionConverter=self.exceptionConverter,status=200,contentType="application/pollapli.node+json",resource="node")
        d=RequestParser(request,"node",self.valid_contentTypes,self.validGetParams).ValidateAndParseParams()
        d.addCallbacks(extract_args,errback=r._build_response)
        d.addBoth(r._build_response)     
        return NOT_DONE_YET
  
    def render_PUT(self,request):
        """
        Handler for PUT requests of node
        """
        @defer.inlineCallbacks
        def extract_args(result):
            print("in extract args",result)
            name=result["name"] or ""
            description=result.get("description") or ""
            id=self.nodeId
            defer.returnValue((yield self.environmentManager.get_environment(self.envId).update_node(id=id,name=name,description=description)))
        
        r=ResponseGenerator(request,exceptionConverter=self.exceptionConverter,status=200,contentType="application/pollapli.node+json",resource="node")
        d=RequestParser(request,"node",self.valid_contentTypes,self.validGetParams).ValidateAndParseParams()    
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
        d=self.environmentManager.get_environment(self.envId).delete_node(self.nodeId)
        d.addBoth(r._build_response)
        return NOT_DONE_YET   
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



class TaskStatusHandler(DefaultRestHandler):
    isLeaf=True
    def __init__(self,rootUri="http://localhost",exceptionConverter=None,environmentManager=None,envId=None,nodeId=None,taskId=None):
        DefaultRestHandler.__init__(self,rootUri,exceptionConverter)
        self.logger=log.PythonLoggingObserver("dobozweb.core.server.rest.connectorStatusHandler")
        self.environmentManager=environmentManager
        self.envId=envId   
        self.nodeId=nodeId
        self.taskId=taskId
        self.valid_contentTypes.append("application/pollapli.task.status+json")   
    
    
    def render_POST(self,request):
        """
        Handler for POST requests of task status
        """
        @defer.inlineCallbacks
        def extract_args(result):
            re
            print("in extract args",result)
            defer.returnValue((yield self.environmentManager.get_environment(self.envId).get_node(self.nodeId).set_connector(**result)))
        
        r=ResponseGenerator(request,exceptionConverter=self.exceptionConverter,status=201,contentType="application/pollapli.task.status+json",resource="taskstatus")
        d=RequestParser(request,"task status",self.valid_contentTypes,self.validGetParams).ValidateAndParseParams()    
        d.addCallbacks(extract_args,errback=r._build_response)    
        d.addBoth(r._build_response)
        return NOT_DONE_YET
#     if params["enabled"]:
#                self.logger.critical("Enabling task %d",self.taskId)
#                self.environmentManager.get_environment(self.envId).get_node(self.nodeId).start_task(self.taskId)
#            else:
#                self.logger.critical("Disabling task %d",self.taskId)
#                self.environmentManager.get_environment(self.envId).get_node(self.nodeId).stop_task(self.taskId)
#           
    
    def render_GET(self, request):
        """
        Handler for GET requests of task status
        """
        def extract_args(result):
            return(self.environmentManager.get_environment(self.envId).get_node(self.nodeId).get_connector())            
        r=ResponseGenerator(request,exceptionConverter=self.exceptionConverter,status=200,contentType="application/pollapli.task.status+json",resource="taskstatus")
        d=RequestParser(request,"task status",self.valid_contentTypes,self.validGetParams).ValidateAndParseParams()
        d.addCallbacks(extract_args,errback=r._build_response)
        d.addBoth(r._build_response)     
        return NOT_DONE_YET
  
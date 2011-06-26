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
from doboz_web.core.server.rest.task_status_handler import TaskStatusHandler

class TaskHandler(DefaultRestHandler):
    """
    Resource in charge of handling the tasks (plural) so :
    Adding a new task
    Listing all tasks
    """
    isLeaf=False
    def __init__(self,rootUri="http://localhost",exceptionConverter=None,environmentManager=None,envId=None,nodeId=None,taskId=None):
        DefaultRestHandler.__init__(self,rootUri,exceptionConverter)
        self.logger=log.PythonLoggingObserver("dobozweb.core.server.rest.taskHandler")
        self.environmentManager=environmentManager
        self.envId=envId
        self.nodeId=nodeId
        self.taskId=taskId
        self.valid_contentTypes.append("application/pollapli.task+json")   
        self.validGetParams.append('id')
        #self.validGetParams.append('type')
        subPath=self.rootUri+"/status"
        self.putChild("status",TaskStatusHandler(subPath,self.exceptionConverter,self.environmentManager,self.envId,self.nodeId,self.taskId)  
)

    
    def render_POST(self,request):  
        """
        Handler for POST requests of tasks
        extract the data from the request body to add a new task
        """ 
        @defer.inlineCallbacks
        def extract_args(result):
            name=result["name"] or ""
            description=result.get("description") or ""
            type=result.get("type") 
            params=result.get("params")
            defer.returnValue((yield self.environmentManager.get_environment(self.envId).get_node(self.nodeId).add_task(name=name,description=description,type=type,params=params)))
             
        r=ResponseGenerator(request,exceptionConverter=self.exceptionConverter,status=201,contentType="application/pollapli.task+json",resource="task")
        d=RequestParser(request,"task",self.valid_contentTypes,self.validGetParams).ValidateAndParseParams()    
        d.addCallbacks(extract_args,errback=r._build_response)    
        d.addBoth(r._build_response)
        return NOT_DONE_YET
    
    def render_GET(self, request):
        """
        Handler for GET requests of tasks
        """
        r=ResponseGenerator(request,exceptionConverter=self.exceptionConverter,status=200,contentType="application/pollapli.task+json",resource="task")
        d=RequestParser(request,"task",self.valid_contentTypes,self.validGetParams).ValidateAndParseParams()
        d.addCallbacks(self.environmentManager.get_environment(self.envId).get_node(self.nodeId).get_tasks,errback=r._build_response)
        d.addBoth(r._build_response)
        return NOT_DONE_YET
    
    def render_DELETE(self,request):
        """ 
        Handler for DELETE requests of tasks
        WARNING !! needs to be used very carefully, with confirmation on the client side, as it deletes ALL
        tasks within a node
        """
        r=ResponseGenerator(request,exceptionConverter=self.exceptionConverter,status=200)
        d= self.environmentManager.get_environment(self.envId).clear_nodes()
        d.addBoth(r._build_response)
        return NOT_DONE_YET   
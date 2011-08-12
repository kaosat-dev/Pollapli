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


class TasksHandler(DefaultRestHandler):
    """
    Resource in charge of handling the tasks (plural) so :
    Adding a new task
    Listing all tasks
    """
    isLeaf=False
    def __init__(self,rootUri="http://localhost",environmentManager=None,envId=None):
        DefaultRestHandler.__init__(self,rootUri)
        self.logger=log.PythonLoggingObserver("dobozweb.core.server.rest.tasksHandler")
        self.environmentManager=environmentManager
        self.envId=envId
        self.valid_contentTypes.append("application/pollapli.taskList+json")   
        self.validGetParams.append('id')
        #self.validGetParams.append('type')
       
      
    def getChild(self, id, request):
        try:
            return TaskHandler(self.rootUri,self.environmentManager,self.envId,int(id))  
        except ValueError :
             return self#no id , so return self
    
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
            defer.returnValue((yield self.environmentManager.get_environment(self.envId).add_task(name=name,description=description,type=type,params=params)))
             
        r=ResponseGenerator(request,status=201,contentType="application/pollapli.task+json",resource="task",rootUri=self.rootUri)
        d=RequestParser(request,"task",self.valid_contentTypes,self.validGetParams).ValidateAndParseParams()    
        d.addCallbacks(extract_args,errback=r._build_response)    
        d.addBoth(r._build_response)
        request._call=reactor.callLater(0,d.callback,None)
        return NOT_DONE_YET
    
    def render_GET(self, request):
        """
        Handler for GET requests of tasks
        """
        r=ResponseGenerator(request,status=200,contentType="application/pollapli.taskList+json",resource="tasks",rootUri=self.rootUri)
        d=RequestParser(request,"task",self.valid_contentTypes,self.validGetParams).ValidateAndParseParams()
        d.addCallbacks(self.environmentManager.get_environment(self.envId).get_tasks,errback=r._build_response)
        d.addBoth(r._build_response)
        request._call=reactor.callLater(0,d.callback,None)
        return NOT_DONE_YET
    
    def render_DELETE(self,request):
        """ 
        Handler for DELETE requests of tasks
        WARNING !! needs to be used very carefully, with confirmation on the client side, as it deletes ALL
        tasks within a node
        """
        r=ResponseGenerator(request,status=200)
        d= self.environmentManager.get_environment(self.envId).clear_nodes()
        d.addBoth(r._build_response)
        request._call=reactor.callLater(0,d.callback,None)
        return NOT_DONE_YET
    
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""  
Single task rest handler
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
class TaskHandler(DefaultRestHandler):
    """
    Resource in charge of handling the tasks (plural) so :
    Adding a new task
    Listing all tasks
    """
    isLeaf=False
    def __init__(self,rootUri="http://localhost",environmentManager=None,envId=None,taskId=None):
        DefaultRestHandler.__init__(self,rootUri)
        self.logger=log.PythonLoggingObserver("dobozweb.core.server.rest.taskHandler")
        self.environmentManager=environmentManager
        self.envId=envId
        self.taskId=taskId
        self.valid_contentTypes.append("application/pollapli.task+json")   
        self.validGetParams.append('id')
        #self.validGetParams.append('type')
        subPath=self.rootUri+"/status"
        self.putChild("status",TaskStatusHandler(subPath,self.environmentManager,self.envId,self.taskId)  
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
            defer.returnValue((yield self.environmentManager.get_environment(self.envId).add_task(name=name,description=description,type=type,params=params)))
             
        r=ResponseGenerator(request,status=201,contentType="application/pollapli.task+json",resource="task",rootUri=self.rootUri)
        d=RequestParser(request,"task",self.valid_contentTypes,self.validGetParams).ValidateAndParseParams()    
        d.addCallbacks(extract_args,errback=r._build_response)    
        d.addBoth(r._build_response)
        request._call=reactor.callLater(0,d.callback,None)
        return NOT_DONE_YET
    
    def render_GET(self, request):
        """
        Handler for GET requests of tasks
        """
        r=ResponseGenerator(request,status=200,contentType="application/pollapli.task+json",resource="task",rootUri=self.rootUri)
        d=RequestParser(request,"task",self.valid_contentTypes,self.validGetParams).ValidateAndParseParams()
        d.addCallbacks(self.environmentManager.get_environment(self.envId).get_tasks,errback=r._build_response)
        d.addBoth(r._build_response)
        request._call=reactor.callLater(0,d.callback,None)
        return NOT_DONE_YET
    
    def render_DELETE(self,request):
        """ 
        Handler for DELETE requests of tasks
        WARNING !! needs to be used very carefully, with confirmation on the client side, as it deletes ALL
        tasks within a node
        """
        r=ResponseGenerator(request,status=200)
        d= self.environmentManager.get_environment(self.envId).clear_nodes()
        d.addBoth(r._build_response)
        request._call=reactor.callLater(0,d.callback,None)
        return NOT_DONE_YET  
    
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""  
Task status rest handler
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
class TaskStatusHandler(DefaultRestHandler):
    isLeaf=True
    def __init__(self,rootUri="http://localhost",environmentManager=None,envId=None,taskId=None):
        DefaultRestHandler.__init__(self,rootUri)
        self.logger=log.PythonLoggingObserver("dobozweb.core.server.rest.taskStatusHandler")
        self.environmentManager=environmentManager
        self.envId=envId   
        self.taskId=taskId
        self.valid_contentTypes.append("application/pollapli.task.status+json")   
    
    
    def render_POST(self,request):
        """
        Handler for POST requests of task status
        """
        @defer.inlineCallbacks
        def extract_args(result):
            start=result.get("start")
            pause=result.get("pause")
            stop=result.get("stop")
            print("task status: start",start,"pause",pause,"stop",stop)
            if start:
                defer.returnValue((yield self.environmentManager.get_environment(self.envId).get_task(self.taskId).start()))
            elif pause:
                defer.returnValue((yield self.environmentManager.get_environment(self.envId).get_task(self.taskId).pause()))
            elif stop:
                defer.returnValue((yield self.environmentManager.get_environment(self.envId).get_task(self.taskId).stop()))
            
        r=ResponseGenerator(request,status=201,contentType="application/pollapli.task.status+json",resource="taskstatus",rootUri=self.rootUri)
        d=RequestParser(request,"task status",self.valid_contentTypes,self.validGetParams).ValidateAndParseParams()    
        d.addCallbacks(extract_args,errback=r._build_response)    
        d.addBoth(r._build_response)
        request._call=reactor.callLater(0,d.callback,None)
        return NOT_DONE_YET
       
    
    def render_GET(self, request):
        """
        Handler for GET requests of task status
        """
        def extract_args(result):
            return(self.environmentManager.get_environment(self.envId).get_task(self.taskId).status)            
        r=ResponseGenerator(request,status=200,contentType="application/pollapli.task.status+json",resource="taskstatus",rootUri=self.rootUri)
        d=RequestParser(request,"task status",self.valid_contentTypes,self.validGetParams).ValidateAndParseParams()
        d.addCallbacks(extract_args,errback=r._build_response)
        d.addBoth(r._build_response)    
        request._call=reactor.callLater(0,d.callback,None) 
        return NOT_DONE_YET
  
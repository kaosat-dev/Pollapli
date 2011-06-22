from twisted.web.server import Site
from twisted.web.resource import Resource
from twisted.internet import reactor
from twisted.web.resource import NoResource
from twisted.python import log
from twisted.python.log import PythonLoggingObserver
import logging
import sys

class Task(object):
    def __init__(self,id=None):
        self.id=id

class Node(object):
    def __init__(self,id,name):
        self.id=id
        self.name=name
        self.tasks=[]
    def add_task(self):
        self.tasks.append(Task(0))
    def remove_task(self,id):
        self.tasks.remove(id)
        
class Environment(object):
    def __init__(self,id,name):
        self.id=id
        self.name=name
        self.nodes={}
    def add_node(self,id,name):
        self.nodes[id]=Node(id,name)
    def remove_node(self,id):
        del self.nodes[id]
        
        
#environments={}
#env=Environment(12,"Aquarium")
#env.add_node(0, "Reprap")
#env.add_node(1,"hydroduino")
#
#env2=Environment(13,"Garden")
#env2.add_node(0, "Huxley")
#environments[12]=env
#environments[13]=env2
##################################
class NoRestResource(Resource):
      def render_GET(self, request):
          request.setResponseCode(412)
          return "<html><body>No such resource.</body></html>"

####################""
class EnvironmentHandler(Resource):
    isLeaf=False
    def __init__(self,id):
        Resource.__init__(self)
        self.id=id
        self.putChild("nodes",HardwareNodesHandler(id))
    
    def render_GET(self,request):
        log.msg("This is important!", logLevel=logging.CRITICAL)
        return "<html><body><pre>Get in env with id: %s</pre></body></html>" % (environments[self.id].name,)
    def render_POST(self,request):
        pass
    def render_PUT(self,request):
        pass
    def render_DELETE(self,request):
        pass
    
class EnvironmentsHandler(Resource):
    isLeaf=False
    def __init__(self):
        Resource.__init__(self)
    def getChild(self, id, request):
        try:
            return EnvironmentHandler(int(id))    
        except ValueError :
             return self#no id , so return self
           
    def render_GET(self,request):
        log.msg("This is important! sdfsdfds", logLevel=logging.CRITICAL)
        return "<html><body><pre>Environements: %s</pre></body></html>" % (str(environments.values()),) 
    def render_POST(self,request):
        pass
    def render_PUT(self,request):
        pass
    def render_DELETE(self,request):
        pass
##################################
class HardwareNodeHandler(Resource):
    isLeaf=False
    def __init__(self,envId,id):
        Resource.__init__(self)
        self.envId=envId
        self.id=id
        self.putChild("tasks",AutomationsHandler(self.envId,id))
    
    def render_GET(self,request):
        return "<html><body><pre>Get in env : %s node: %s</pre></body></html>" % (environments[self.envId].name,environments[self.envId].nodes[self.id].name,)
    def render_POST(self,request):
        pass
    def render_PUT(self,request):
        pass
    def render_DELETE(self,request):
        pass
    
class HardwareNodesHandler(Resource):
    isLeaf=False
    def __init__(self,envId):
        Resource.__init__(self)
        self.envId=envId
        
    def getChild(self, id, request):
        try:
            return HardwareNodeHandler(self.envId,int(id))    
        except:
            return NoResource()
    def render_GET(self,request):
        return "<html><body><pre>Nodes</pre></body></html>" 
    def render_POST(self,request):
        pass
    def render_PUT(self,request):
        pass
    def render_DELETE(self,request):
        pass
    
##################################
class AutomationHandler(Resource):
    isLeaf=False
    def __init__(self,envId,nodeId,id):
        Resource.__init__(self)
        self.envId=envId
        self.nodeId=nodeId
        self.id=id
        
 
    
    def render_GET(self,request):
        return "<html><body><pre>Get in env : %s node : %s, task: %s</pre></body></html>" % (environments[self.envId].name,environments[self.envId].nodes[self.nodeId].name,self.id)
    def render_POST(self,request):
        pass
    def render_PUT(self,request):
        pass
    def render_DELETE(self,request):
        pass
    
class AutomationsHandler(Resource):
    isLeaf=False
    def __init__(self,envId,nodeId):
        Resource.__init__(self)
        self.envId=envId
        self.nodeId=nodeId
        
    def getChild(self, id, request):
        try:
            return AutomationHandler(self.envId,self.nodeId,int(id))    
        except:
            pass
    def render_GET(self,request):
        return "<html><body><pre>Tasks</pre></body></html>" 
    def render_POST(self,request):
        pass
    def render_PUT(self,request):
        pass
    def render_DELETE(self,request):
        pass



#root = Resource()
#
#factory = Site(root)
#reactor.listenTCP(8008, factory)
#reactor.run()
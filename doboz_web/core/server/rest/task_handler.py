from doboz_web.core.server.rest.base_rest_handler import BaseRestHandler
from doboz_web.core.server.bottle import  response 

class TaskRestHandler(BaseRestHandler):
    def __init__(self,rootUri="http://localhost",environmentManager=None,envId=None,nodeId=None,taskId=None):
        BaseRestHandler.__init__(self)
        self.rootUri=rootUri
        self.environmentManager=environmentManager
        self.envId=envId
        self.nodeId=nodeId
        self.taskId=taskId
        
    def render_GET(self, request):
        self.logger.critical("Using task GET handler")
        if request.headers.get("Content-Type")=="application/json":
            callback=request.GET.get('callback', '').strip()
            resp=callback+"()"
            resp=""
            try:
                task=self.environmentManager.get_environment(self.envId).get_node(self.nodeId).get_task(self.taskId)
                if task:
                    lnk='{"link" : {"href":"'+self.rootUri+str(task.id)+'", "rel": "task"},'
                    resp='{"Task":'+lnk+task._toJson()+'}}'
                else:
                    response.status=500
                    error='{"error":{"id":0,"message":"failed to add task"}}'
                    resp='{"Tasks":'+error+'}'
            except Exception as inst:
                self.logger.critical("in env %d node id %d task post error: %s",self.envId,self.nodeId, str(inst))
            finally:
                return resp
        else:
            abort(501,"Not Implemented")
                
    def render_PUT(self,request):
        resp=""
        try:
            task=self.environmentManager.get_environment(self.envId).get_node(self.nodeId).add_task(**self._fetch_jsonData(request))
            if task:
                lnk='{"link" : {"href":"'+self.rootUri+str(task.id)+'", "rel": "task"},'
                resp='{"Task":'+lnk+task._toJson()+'}}'
            else:
                response.status=500
                error='{"error":{"id":0,"message":"failed to add task"}}'
                resp='{"Tasks":'+error+'}'
        except Exception as inst:
            self.logger.critical("in env %d node id %d task post error: %s",self.envId,self.nodeId, str(inst))
        finally:
            return resp
        
    def render_DELETE(self,request):
        try:
            self.environmentManager.get_environment(self.envId).get_node(self.nodeId).remove_task(self.taskId)
        except Exception as inst:
            self.logger.critical("in env %s node id %d task clear error: %s",self.envId,self.nodeId, str(inst))
            abort(500,"Failed to clear tasks")
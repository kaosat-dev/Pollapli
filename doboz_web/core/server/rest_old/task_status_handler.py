from doboz_web.core.server.rest.base_rest_handler import BaseRestHandler
from doboz_web.core.server.bottle import  response 

class TaskStatusRestHandler(BaseRestHandler):
    def __init__(self,rootUri="http://localhost",environmentManager=None,envId=None,nodeId=None,taskId=None):
        BaseRestHandler.__init__(self)
        self.rootUri=rootUri
        self.environmentManager=environmentManager
        self.envId=envId
        self.nodeId=nodeId
        self.taskId=taskId
        
    def render_GET(self, request):
        self.logger.critical("Using task status GET handler")
        if request.headers.get("Content-Type")=="application/json":
            callback=request.GET.get('callback', '').strip()
            response=callback+"()"
            try:
                #self.environmentManager.get_environment(self.envId).get_node(self.nodeId).connector
                response=callback+"('Environment':"+self.envId+",'Node':"+str(self.nodeId)+",'Status':{'Active':true,'Progress':56,'Components':{})"
            except Exception as inst:
                self.logger.critical("Failed to get connector status error: %s",str(inst))
                abort(500,"Failed to get connector status info ")
            return response
        else:
            abort(501,"Not Implemented")
        
            
    def render_POST(self, request):
        try:
            params=self._fetch_jsonData(request)
            #task=self.environmentManager.get_environment(self.envId).get_node(self.nodeId).get_task(self.taskId)
            if params["enabled"]:
                self.logger.critical("Enabling task %d",self.taskId)
                self.environmentManager.get_environment(self.envId).get_node(self.nodeId).start_task(self.taskId)
            else:
                self.logger.critical("Disabling task %d",self.taskId)
                self.environmentManager.get_environment(self.envId).get_node(self.nodeId).stop_task(self.taskId)
                
        except Exception as inst:
            self.logger.critical("in env %s  node %d task %d put error: %s",self.envId,self.nodeId,self.taskId, str(inst))
            abort(500,"error in enabling task")
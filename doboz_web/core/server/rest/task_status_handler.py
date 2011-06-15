from doboz_web.core.server.rest.base_rest_handler import BaseRestHandler

class TaskStatusRestHandler(BaseRestHandler):
    def __init__(self,environmentManager=None,envName=None,nodeId=None,taskId=None):
        BaseRestHandler.__init__(self)
        self.environmentManager=environmentManager
        self.envName=envName
        self.nodeId=nodeId
        self.taskId=taskId
        
    def render_GET(self, request):
        self.logger.critical("Using task status GET handler")
        if request.headers.get("Content-Type")=="application/json":
            callback=request.GET.get('callback', '').strip()
            response=callback+"()"
            try:
                #self.environmentManager.get_environment(self.envName).get_node(self.nodeId).connector
                response=callback+"('Environment':"+self.envName+",'Node':"+str(self.nodeId)+",'Status':{'Active':true,'Progress':56,'Components':{})"
            except Exception as inst:
                self.logger.critical("Failed to get connector status error: %s",str(inst))
                abort(500,"Failed to get connector status info ")
            return response
        else:
            abort(501,"Not Implemented")
        
            
    def render_POST(self, request):
        try:
            params=self._fetch_jsonData(request)
            if params["enabled"]:
                #self.logger.critical("Enabling task %d",self.taskId)
                self.environmentManager.get_environment(self.envName).get_node(self.nodeId).connect()
            else:
                self.logger.critical("Disabling task %d",self.taskId)
                #self.environmentManager.get_environment(self.envName).get_node(self.nodeId).disconnect()
                
        except Exception as inst:
            self.logger.critical("in env %s  node %d task %d put error: %s",self.envName,self.nodeId,self.taskId, str(inst))
            abort(500,"error in enabling task")
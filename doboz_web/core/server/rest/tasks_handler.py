from doboz_web.core.server.rest.base_rest_handler import BaseRestHandler

class TasksRestHandler(BaseRestHandler):
    def __init__(self,environmentManager=None,envName=None,nodeId=None):
        BaseRestHandler.__init__(self)
        self.environmentManager=environmentManager
        self.envName=envName
        self.nodeId=nodeId
        
    def render_GET(self, request):
        self.logger.critical("Using tasks GET handler")
        if request.headers.get("Content-Type")=="application/json":
            callback=request.GET.get('callback', '').strip()
            response=callback+"()"
            return response
        else:
            abort(501,"Not Implemented")
    def render_POST(self,request):
        try:
            self.environmentManager.get_environment(self.envName).get_node(self.nodeId).add_task(**self._fetch_jsonData(request))
        except Exception as inst:
            self.logger.critical("in env %s node id %d task post error: %s",self.envName,self.nodeId, str(inst))
     
    def render_DELETE(self,request):
        try:
            self.environmentManager.get_environment(self.envName).get_node(self.nodeId).clear_tasks()
        except Exception as inst:
            self.logger.critical("in env %s node id %d task clear error: %s",self.envName,self.nodeId, str(inst))
            abort(500,"Failed to clear tasks")
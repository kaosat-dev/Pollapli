from doboz_web.core.server.rest.base_rest_handler import BaseRestHandler

class TaskComponentRestHandler(BaseRestHandler):
    def __init__(self,environmentManager=None,envName=None,nodeId=None,taskId=None):
        BaseRestHandler.__init__(self)
        self.environmentManager=environmentManager
        self.envName=envName
        self.nodeId=nodeId
        self.taskId=taskId
        
    def render_GET(self, request):
        self.logger.critical("Using task GET handler")
        if request.headers.get("Content-Type")=="application/json":
            callback=request.GET.get('callback', '').strip()
            response=callback+"()"
            return response
        else:
            abort(501,"Not Implemented")
            
    def render_DELETE(self,request):
        try:
            self.environmentManager.get_environment(self.envName).get_node(self.nodeId).remove_task(self.taskId)
        except Exception as inst:
            self.logger.critical("in env %s  node %d task delete error: %s",self.envName,self.nodeId, str(inst))
            abort(500,"Failed to delete task")
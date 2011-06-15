from doboz_web.core.server.rest.base_rest_handler import BaseRestHandler
from doboz_web.core.server.bottle import Bottle, request, response 

class NodesRestHandler(BaseRestHandler):
    def __init__(self,environmentManager=None,envId=None):
        BaseRestHandler.__init__(self)
        self.environmentManager=environmentManager
        self.envId=envId
        
    def render_GET(self, request):
        self.logger.critical("Using nodes GET handler")
        if request.headers.get("Content-Type")=="application/json":
            callback=request.GET.get('callback', '').strip()
            resp=callback+"()"
            try:
                data=self.environmentManager.get_environment(self.envId).get_nodes()
                resp=callback+'{"Environment":'+str(self.envId)+',"Nodes":'+str(data)+'}'
            except Exception as inst:
                self.logger.critical("environment %d nodes get error %s",self.envId, str(inst))
                abort(500,"error in getting environment info")
            response.content_type = 'application/json'
            return resp
        else:
            abort(501,"Not Implemented")
            
    def render_POST(self,request):
        try:
            self.environmentManager.get_environment(self.envId).add_node(**self._fetch_jsonData(request))
        except Exception as inst:
            self.logger.critical("in env %s  node post error: %s",self.envId, str(inst))
            abort(500,"error in adding node")
        
    def render_DELETE(self,request):
        try:
            self.environmentManager.get_environment(self.envId).clear_nodes()
        except Exception as inst:
            self.logger.critical("nodes deletion error %s",str(inst))
            abort(500,"Failed to delete nodes")
from doboz_web.core.server.rest.base_rest_handler import BaseRestHandler

class ConnectorRestHandler(BaseRestHandler):
    def __init__(self,environmentManager=None,envName=None,nodeId=None):
        BaseRestHandler.__init__(self)
        self.environmentManager=environmentManager
        self.envName=envName
        self.nodeId=nodeId
        
    def render_GET(self, request):
        self.logger.critical("Using connector GET handler")
        if request.headers.get("Content-Type")=="application/json":
            callback=request.GET.get('callback', '').strip()
            response=callback+"()"
            return response
        else:
            abort(501,"Not Implemented")
    def render_PUT(self, request):
        try:
            self.environmentManager.get_environment(self.envName).get_node(self.nodeId).set_connector(**self._fetch_jsonData(request))
        except Exception as inst:
            self.logger.critical("in env %s  node %d connector put error: %s",self.envName,self.nodeId, str(inst))
            abort(500,"error in setting connector")
            
    def render_DELETE(self,request):
        try:
            pass#self.environmentManager.get_environment(self.envName).delete_node(self.nodeId)
        except Exception as inst:
            self.logger.critical("in env %s  node %d connector delete error: %s",self.envName,self.nodeId, str(inst))
            abort(500,"Failed to delete connector")
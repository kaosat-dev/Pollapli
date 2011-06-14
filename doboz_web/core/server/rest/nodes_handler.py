from doboz_web.core.server.rest.base_rest_handler import BaseRestHandler

class NodesRestHandler(BaseRestHandler):
    def __init__(self,environmentManager=None,envName=None):
        BaseRestHandler.__init__(self)
        self.environmentManager=environmentManager
        self.envName=envName
        
    def render_GET(self, request):
        self.logger.critical("Using nodes GET handler")
        if request.headers.get("Content-Type")=="application/json":
            callback=request.GET.get('callback', '').strip()
            response=callback+"()"
            try:
                data=self.environmentManager.get_environment(self.envName).get_nodes()
                response=callback+"(Environment:"+self.envName+",Nodes:("+str(data)+"))"
            except Exception as inst:
                self.logger.critical("environment %s nodes get error %s",str(self.envName), str(inst))
                abort(500,"error in getting environment info")
            return response
        else:
            abort(501,"Not Implemented")
            
    def render_POST(self,request):
        try:
            self.environmentManager.get_environment(self.envName).add_node(**self._fetch_jsonData(request))
        except Exception as inst:
            self.logger.critical("in env %s  node post error: %s",self.envName, str(inst))
            abort(500,"error in adding node")
        
    def render_DELETE(self,request):
        try:
            self.environmentManager.get_environment(self.envName).clear_nodes()
        except Exception as inst:
            self.logger.critical("nodes deletion error %s",str(inst))
            abort(500,"Failed to delete nodes")
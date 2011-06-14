from doboz_web.core.server.rest.base_rest_handler import BaseRestHandler

class ConnectorStatusRestHandler(BaseRestHandler):
    def __init__(self,environmentManager=None,envName=None,nodeId=None):
        BaseRestHandler.__init__(self)
        self.environmentManager=environmentManager
        self.envName=envName
        self.nodeId=nodeId
        
    def render_GET(self, request):
        self.logger.critical("Using connector status GET handler")
        if request.headers.get("Content-Type")=="application/json":
            callback=request.GET.get('callback', '').strip()
            response=callback+"()"
            try:
                #self.environmentManager.get_environment(self.envName).get_node(self.nodeId).connector
                response=callback+"('Environment':"+self.envName+",'Node':"+str(self.nodeId)+",'Connector':'serial','Connected':true)"
            except Exception as inst:
                self.logger.critical("Failed to get connector status error: %s",str(inst))
                abort(500,"Failed to get connector status info ")
            return response
        else:
            abort(501,"Not Implemented")
            
    def render_POST(self, request):
        try:
            params=self._fetch_jsonData(request)
            if params["connected"]:
                self.logger.critical("Connecting node %d",self.nodeId)
                self.environmentManager.get_environment(self.envName).get_node(self.nodeId).connect()
            else:
                self.logger.critical("Disconnecting node %d",self.nodeId)
                self.environmentManager.get_environment(self.envName).get_node(self.nodeId).disconnect()
                
        except Exception as inst:
            self.logger.critical("in env %s  node %d connector put error: %s",self.envName,self.nodeId, str(inst))
            abort(500,"error in setting connector")
    
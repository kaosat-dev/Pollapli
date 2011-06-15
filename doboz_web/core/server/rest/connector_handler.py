import logging 

from doboz_web.core.server.rest.base_rest_handler import BaseRestHandler
from doboz_web.core.server.bottle import response 

class ConnectorRestHandler(BaseRestHandler):
    def __init__(self,environmentManager=None,envId=None,nodeId=None):
        BaseRestHandler.__init__(self)
        self.logger=logging.getLogger("dobozweb.core.server.connectorhandler")
        self.environmentManager=environmentManager
        self.envId=envId
        self.nodeId=nodeId
        
    def render_GET(self, request):
        self.logger.critical("Using connector GET handler")
        if request.headers.get("Content-Type")=="application/json":
            callback=request.GET.get('callback', '').strip()
            resp=callback+"()"
            response.content_type = 'application/json'
            return resp
        else:
            abort(501,"Not Implemented")
    def render_PUT(self, request):
        try:
            self.environmentManager.get_environment(self.envId).get_node(self.nodeId).set_connector(**self._fetch_jsonData(request))
        except Exception as inst:
            self.logger.critical("in env %s  node %d connector put error: %s",self.envId,self.nodeId, str(inst))
            abort(500,"error in setting connector")
            
    def render_DELETE(self,request):
        self.logger.critical("Using connector DELETE handler")
        try:
            self.environmentManager.get_environment(self.envId).get_node(self.nodeId).remove_connector()
        except Exception as inst:
            self.logger.critical("in env %s  node %d connector delete error: %s",self.envId,self.nodeId, str(inst))
            abort(500,"Failed to delete connector")
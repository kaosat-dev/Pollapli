from doboz_web.core.server.rest.base_rest_handler import BaseRestHandler
from doboz_web.core.server.bottle import  response 

class NodesRestHandler(BaseRestHandler):
    def __init__(self,rootUri="http://localhost",environmentManager=None,envId=None):
        BaseRestHandler.__init__(self)
        self.rootUri=rootUri
        self.environmentManager=environmentManager
        self.envId=envId
        
    def render_GET(self, request):
        self.logger.critical("Using nodes GET handler")
        if request.headers.get("Content-Type")=="application/json":
            callback=request.GET.get('callback', '').strip()
            resp=callback+"()"
            try:
                nodesData=self.environmentManager.get_environment(self.envId).get_nodes()
                tmp=[]
                for node in nodesData:
                    lnk='{"link" : {"href":"'+self.rootUri+str(node.id)+'", "rel": "node"},'
                    tmp.append(lnk+node._toJson()+'}')
                resp=callback+'{"Nodes List":{"link":{"href":"'+self.rootUri+'", "rel": "nodes"}},"items":['+','.join(tmp)+']}'
                response.content_type = 'application/json'
            except Exception as inst:
                self.logger.exception("Error in nodes get %s",str(inst))
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
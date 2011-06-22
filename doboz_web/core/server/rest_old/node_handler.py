from doboz_web.core.server.rest.base_rest_handler import BaseRestHandler
from doboz_web.core.server.bottle import  response 

class NodeRestHandler(BaseRestHandler):
    def __init__(self,rootUri="http://localhost",environmentManager=None,envId=None,nodeId=None):
        BaseRestHandler.__init__(self)
        self.rootUri=rootUri
        self.environmentManager=environmentManager
        self.envId=envId
        self.nodeId=nodeId
        
    def render_GET(self, request):
        self.logger.critical("Using node GET handler")
        if request.headers.get("Content-Type")=="application/json":
            callback=request.GET.get('callback', '').strip()
            resp=callback+"()"
            resp=""
            try:
                node=self.environmentManager.get_environment(self.envId).get_node(self.nodeId)
                if node:
                    lnk='{"link" : {"href":"'+self.rootUri+str(node.id)+'", "rel": "node"},'
                    resp='{"Node":'+lnk+node._toJson()+'}}'
                else:
                    response.status=500
                    error='{"error":{"id":0,"message":"failed to get node"}}'
                    resp='{"Tasks":'+error+'}'
            except Exception as inst:
                self.logger.critical("in env %d node id %d task post error: %s",self.envId,self.nodeId, str(inst))
                response.status=500
            finally:
                return resp
        else:
            abort(501,"Not Implemented")
            
    def render_DELETE(self,request):
        try:
            self.environmentManager.get_environment(self.envId).delete_node(self.nodeId)
        except Exception as inst:
            self.logger.critical("in env %s  node %d connector delete error: %s",self.envId,self.nodeId, str(inst))
            abort(500,"Failed to delete environments")
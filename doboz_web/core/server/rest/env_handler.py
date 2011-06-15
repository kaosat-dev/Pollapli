from doboz_web.core.server.rest.base_rest_handler import BaseRestHandler
from doboz_web.core.server.bottle import  response 

class EnvRestHandler(BaseRestHandler):
    def __init__(self,rootUri="http://localhost",environmentManager=None,envId=None):
        BaseRestHandler.__init__(self)
        self.rootUri=rootUri
        self.environmentManager=environmentManager
        self.envId=envId
        
    def render_GET(self, request):
        self.logger.critical("Using env GET handler")
        if request.headers.get("Content-Type")=="application/json":
            callback=request.GET.get('callback', '').strip()
            resp=callback+"()"
            try:
                env=self.environmentManager.get_environment(self.envId)
                lnk='{"link" : {"href":"'+self.rootUri+str(env.id)+'", "rel": "environment"},'
                resp='{"Environment":'+lnk+env._toJson()+'}}'
            except Exception as inst:
                self.logger.critical("environment %s get error %s",str(self.envId), str(inst))
                abort(500,"error in getting environment info")
                
            response.content_type = 'application/json'
            return resp
        else:
            abort(501,"Not Implemented")
       
    def render_PUT(self,request):
        try:       
            self.environmentManager.add_environment(**self._fetch_jsonData(request))
        except Exception as inst:
            self.logger.critical("error %s",str(inst))
            abort(500,"error in adding environment")
            
    def render_DELETE(self,request):
        try:
            self.environmentManager.remove_environment(self.envId)
        except Exception as inst:
            self.logger.critical("environment deletion error %s",str(inst))
            abort(500,"Failed to delete environments")
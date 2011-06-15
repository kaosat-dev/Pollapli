from doboz_web.core.server.base_rest_handler import BaseRestHandler
from doboz_web.core.server.bottle import Bottle, request, response 

class EnvRestHandler(BaseRestHandler):
    def __init__(self,environmentManager=None,envId=None):
        BaseRestHandler.__init__(self)
        self.environmentManager=environmentManager
        self.envId=envId
        
    def render_GET(self, request):
        self.logger.critical("Using env GET handler")
        if request.headers.get("Content-Type")=="application/json":
            callback=request.GET.get('callback', '').strip()
            resp=callback+"()"
            try:
                resp=callback+"("+str(self.environmentManager.get_environementInfo(self.envId))+")"
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
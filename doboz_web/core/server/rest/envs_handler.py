from doboz_web.core.server.rest.base_rest_handler import BaseRestHandler

class EnvsRestHandler(BaseRestHandler):
    def __init__(self,environmentManager=None):
        BaseRestHandler.__init__(self)
        self.environmentManager=environmentManager
        
    def render_GET(self, request):
        self.logger.critical("Using envs GET handler")
        if request.headers.get("Content-Type")=="application/json":
              callback=request.GET.get('callback', '').strip()
              response=callback+"()"
              try:
                  envData=self.environmentManager.get_environments()
                  envStr=['"'+str(env)+'"' for env in envData]
                  response=callback+'{"Environments":['+','.join(envStr)+']}'
              except Exception as inst:
                  self.logger.exception("Error in envs get %s",str(inst))
                  abort(500,"error in getting environments")
              return response
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
            self.environmentManager.clear_environments()
        except Exception as inst:
            self.logger.critical("environment deletion error %s",str(inst))
            abort(500,"Failed to delete environments")
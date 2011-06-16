import logging
from doboz_web.core.server.rest.base_rest_handler import BaseRestHandler
from doboz_web.core.server.bottle import Bottle, request, response 

class EnvsRestHandler(BaseRestHandler):
    def __init__(self,rootUri="http://localhost",environmentManager=None):
        BaseRestHandler.__init__(self,rootUri)
        self.logger=logging.getLogger("dobozweb.core.server.rest.environmentsHandler")
        self.environmentManager=environmentManager
        self.valid_contentTypes.append("application/pollapli.environmentsList+json")   
             
    def render_GET(self, request):
#        tutu={}
#        tutu.keys()
#        tutu.itervalues()
        print(request.GET.keys())
        #print(request.GET.values())
        test=request.GET.getall("id")
        test2=request.GET.getall("active")
        filterCriteria={}
        filterCriteria["id"]=[int(id)for id in test]
        #filterCriteria["active"]=[id.lower() in ("true") for id in test2]
        filterCriteria["status"]=test2
      
        payload=self._build_resource_list_uri(self.environmentManager.get_environments(filterCriteria),"environment")
        resp=None
        if payload:
            resp=self._build_response(request,200,payload,contentType="application/pollapli.environmentsList+json")
        else:
            resp=self._build_response(request,500,payload)
        return resp
    
    def render_POST(self,request):
        env=self.environmentManager.add_environment(**self._fetch_jsonData(request))
        payload=self._build_resource_uri(env,"environment")
        resp=self._build_response(request,200,payload,contentType="application/pollapli.environment+json")
        return resp
            
    def render_DELETE(self,request):
        try:
            self.environmentManager.clear_environments()
        except Exception as inst:
            self.logger.critical("environment deletion error %s",str(inst))
            abort(500,"Failed to delete environments")
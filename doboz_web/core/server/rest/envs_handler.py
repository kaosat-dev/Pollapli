from doboz_web.core.server.rest.base_rest_handler import BaseRestHandler
from doboz_web.core.server.bottle import Bottle, request, response 

class EnvsRestHandler(BaseRestHandler):
    def __init__(self,environmentManager=None):
        BaseRestHandler.__init__(self)
        self.environmentManager=environmentManager
        
    def render_GET(self, request):
        self.logger.critical("Using envs GET handler")
        if request.headers.get("Content-Type")=="application/json":
            callback=request.GET.get('callback', '').strip()
            resp=""
            #response=callback+"()"
            try:
                envData=self.environmentManager.get_environments()
                thingy=[]
                for env in envData:
                    
                    lnk='{"link" : {"href":"http://localhost/environments/'+str(env.id)+'", "rel": "environment"},'
                    tt='"id":'+ str(env.id)+',"name": "'+env.name+'","status":"'+env.status+'"}'
                    thingy.append(lnk+tt)
#                   
                resp=callback+'{"Environments List":{"link":{"href":"http://localhost/environments/", "rel": "environments"}},"items":['+','.join(thingy)+']}'
            except Exception as inst:
                self.logger.exception("Error in envs get %s",str(inst))
                abort(500,"error in getting environments")
            response.content_type = 'application/json'
            return resp
        else:
            abort(501,"Not Implemented")
            
    def render_POST(self,request):
        try:       
            env=self.environmentManager.add_environment(**self._fetch_jsonData(request))
            resp=""
            if env:
                lnk='{"link" : {"href":"http://localhost/environments/'+str(env.id)+'", "rel": "environment"},'
                tt='"id":'+ str(env.id)+',"name": "'+env.name+'"}'
                resp='{"Environment":'+lnk+tt+'}'
                return resp
            else:
                response.status=500
                error='{"error":{"id":0,"message":"failed to create environment"}}'
                resp='{"Environments":'+error+'}'
                return resp
            
        except Exception as inst:
            self.logger.critical("error %s",str(inst))
            response.status=500
            error='{"error":{"id":0,"message":"failed to create environment"}}'
            resp='{"Environments":'+error+'}'
            return resp
            
    def render_DELETE(self,request):
        try:
            self.environmentManager.clear_environments()
        except Exception as inst:
            self.logger.critical("environment deletion error %s",str(inst))
            abort(500,"Failed to delete environments")
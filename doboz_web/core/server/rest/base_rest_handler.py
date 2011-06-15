import json
import logging
from doboz_web.core.server.bottle import Bottle, route, run, send_file, redirect, abort, request, response 

class BaseRestHandler(object):
    def __init__(self):
        self.logger=logging.getLogger("dobozweb.core.server.baseresthandler")
        self.validApplication_types=[]
        self.validApplication_types.append("application/json")
        
    def getChild(self, id, request):
        pass
#        try:
#            return EnvironmentHandler(int(id))    
#        except ValueError :
#             return self
    
    def render_GET(self, request):
        self.logger.critical("Using default GET handler")
        print(request.headers.get("Content-Type"))
        abort(501,"Not Implemented")      
        
        
    def render_POST(self,request):
        self.logger.critical("Using default POST handler")
        abort(501,"Not Implemented")
        
    def render_PUT(self,request):
        self.logger.critical("Using default PUT handler")
        abort(501,"Not Implemented")
        
    def render_DELETE(self,request):
        self.logger.critical("Using default PUT handler")
        abort(501,"Not Implemented")
    
    def _handle(self, request):
        self.logger.critical("Handling request of type %s",str(request.method))
        if request.method=="GET":
            return self.render_GET(request)
        elif request.method=="POST":
            return self.render_POST(request)
        elif request.method=="PUT":
            return self.render_PUT(request)
        elif request.method=="DELETE":
            return self.render_DELETE(request)
    
    def _handle_request(self):
        handlers={}
        handlers["application/json"]=jsonHandler
        handlers["application/xml"]=xmlHandler
        
        content_type=request.headers.get("Content-Type")
        print(content_type)
        if not handlers[content_type]: 
            abort(501,contentTypeErrorMessage)
        else:
            try: 
                handlers[content_type](**data_fetchers[content_type]())
            except Exception as inst:
                server.logger.critical("error %s",str(inst))
                abort(500,errorMessage) 
        
    def _fetch_jsonData(self,request):
        """ In python pre 2.6.5, bug in unicode dict keys"""
        data=request.body.readline()
        
        if data == None or data == '':
            return {}
        else:   
            params=json.loads(data,encoding='utf8')
           
            params=self._stringify_data(params)
        return params 
    
    def _format_jsonResponse():
        callback=request.GET.get('callback', '').strip()
        response=callback+"()"
    
    """Convert any dict keys to str, because of a bug in pre 2.6.5 python"""
    def _stringify_data(self,obj):
        if type(obj) in (int, float, str, bool):
                return obj
        elif type(obj) == unicode:
                return obj#return str(obj)
        elif type(obj) == dict:
                modobj={}
                for i,v in obj.iteritems():
                        modobj[str(i)]=self._stringify_data(v)
                obj=modobj
                       # obj[i] = filter_data(v)
        else:
                print "invalid object in data, converting to string"
                obj = str(obj) 
        return obj   
import json
import logging
from doboz_web.core.server.bottle import Bottle, route, run, send_file, redirect, abort, request, response 


class BaseRestHandler(object):
    def __init__(self,rootUri="http://localhost"):
        self.logger=logging.getLogger("dobozweb.core.server.rest.baseresthandler")
        self.rootUri=rootUri
        self.valid_contentTypes=[]
        
    def getChild(self, id, request):
        pass
    
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
        
        """Here we pre filter the requests based on content type:
        if the content type is not handled by a resource handler,
        don't bother doing anything , and tell client that is not supported
        """
        if request.headers.get("Content-Type") not in self.valid_contentTypes:
            abort(501,"Content Type not supported")
            return None
        
         
        if request.method=="GET":
            return self.render_GET(request)
        elif request.method=="POST":
            return self.render_POST(request)
        elif request.method=="PUT":
            return self.render_PUT(request)
        elif request.method=="DELETE":
            return self.render_DELETE(request)
    
    def _build_response(self,request,status,payload,contentType="text/html"):
        callback=request.GET.get('callback', '').strip() 
        
        response.status=status
        response.content_type=contentType
        
        if callback:
            return callback+"("+payload+")" 
        else:
            return payload
        
    
    
    def _build_resource_uri(self,resourceInstance,resourceName):
        """
        builds the current resource uri /link, based on resource name and root uri
        """
        item={}
        item["link"]={}
        item["link"]["href"]=self.rootUri+str(resourceInstance.id)
        item["link"]["rel"]=resourceName
    
        item=dict(item.items() + resourceInstance._toDict().items())
        return item
    
    def _build_resource_list_uri(self,list,resourceName):
        """
        generates a dictionary based data structure for a set of links in json, based on a list
        and a resource name
        """
        result={}
        try:
            result[ resourceName+"s List"]={}
            result[resourceName+"s List"]["link"]={}
            result[resourceName+"s List"]["link"]["href"]=self.rootUri
            result[resourceName+"s List"]["link"]["rel"]=resourceName+"s"
            result[resourceName+"s List"]["items"]=[self._build_resource_uri(item,resourceName)for item in list] 
        except Exception as inst:
            self.logger.exception(" %s",str(inst))
        return result
        
    
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
import json
import logging

from doboz_web.core.server.bottle import Bottle, route, run, send_file, redirect, abort, request, response 
from doboz_web.core.server.rest.deferred import Deferred


class ResponseMessage(object):
    def __init__(self,payload=None,status=500,resource="",errorCode=0,errorMessage=""):
        self.payload=payload
        self.status=status
        self.resource=resource
        self.errorCode=errorCode
        self.errorMessage=errorMessagem

class BaseRestHandler(object):
    def __init__(self,rootUri="http://localhost"):
        self.logger=logging.getLogger("dobozweb.core.server.rest.baseresthandler")
        self.rootUri=rootUri
        """
        what kind of content types are supported
        """
        self.valid_contentTypes=[]
        """
        what kind of query params does the Get method accept
        """
        self.validGetParams=[]
        
        
    
    def render_GET(self, request):
        """
        Default GET handler
        """
        self.logger.critical("Using default GET handler")
        print(request.headers.get("Content-Type"))
        abort(501,"Not Implemented")      
    
    def render_POST(self,request):
        """
        Default POST handler
        """
        self.logger.critical("Using default POST handler")
        abort(501,"Not Implemented")
        
    def render_PUT(self,request):
        self.logger.critical("Using default PUT handler")
        abort(501,"Not Implemented")
        
    def render_DELETE(self,request):
        self.logger.critical("Using default PUT handler")
        abort(501,"Not Implemented")
    
    def _handle(self, request):
        """
        main access point for request handling
        this method then dispatches the request to the adapted render_
        handler , based on the http method of the request
        """
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
    
    
    def _build_response(self,callback,errback):
        try:
            callback()
        except Exception as inst:
            self.logger.cricital("blaaa %s",str(inst))
            errback()
    
    def _build_valid_response(self,payload,request=None,status=200,contentType="text/html"):
        """
        build a simple response
        """
        
        print("building response")
        #raise Exception("lmkmlk")
        callback=request.GET.get('callback', '').strip() 
        
        response.status=status
        response.content_type=contentType
        print("building payload",payload)
        if callback:
            return callback+"("+payload+")" 
        else:
            return payload
    def _build_valid_response_failure(self,result):
        print("error in building valid response",result.exception)
        return self._build_error_response(status=500,resource="environment",errorCode=3,errorMessage="failed to build valid response!")
        
        
        
    def _build_error_response(self,data,status=500,resource="",errorCode=0,errorMessage=""): 
        """
        builds a custom error response
        """
        response.status=status
        resp={}
        resp["rest_error"]={}
        resp["rest_error"]["error_code"]=errorCode 
        resp["rest_error"]["error_msg"]=errorMessage
        resp["rest_error"]["source"]=self._build_resource_uri(resource)
        
        return resp
    
    def result_dict_extractor(self,result={},callback=None):
        """helper function to pass a result as an unpacked dictionary to a function
        """
        return callback(**result)
    
    def _build_resource_uri(self,resourceInstance=None,resourceName=""):
        """
        builds the current resource uri /link, based on resource name and root uri
        """
        item={}
        item["link"]={}
        item["link"]["rel"]=resourceName
        if resourceInstance:   
            item["link"]["href"]=self.rootUri+str(resourceInstance.id)
            item=dict(item.items() + resourceInstance._toDict().items())
        else:
            item["link"]["href"]=self.rootUri
       
        return item
    def _handle_build_resource_uri_error(self,failure):
        print("Handling build resource uri error",result.exception)
        raise Exception("oh oh")
        return self._build_error_response(status=500,resource="environment",errorCode=0,errorMessage="failed to parse query params!")
       
    
    def _build_resource_list_uri(self,list,resourceName):
        """
        generates a dictionary based data structure for a set of links in json, based on a list
        and a resource name
        """
        result={}
        result[ resourceName+"s List"]={}
        result[resourceName+"s List"]["link"]={}
        result[resourceName+"s List"]["link"]["href"]=self.rootUri
        result[resourceName+"s List"]["link"]["rel"]=resourceName+"s"
        result[resourceName+"s List"]["items"]=[self._build_resource_uri(item,resourceName)for item in list] 
        
        return result
    
    def dummy_test(self,request):
        raise Exception("toto")
        return request
         
    def _parse_query_params(self,request):
        print("here in q param")
        """
        method parses query params into a dictionary of lists for filter criteria
        """
        #raise Exception("aaah failure in parse params")
        #filterCriteria["active"]=[id.lower() in ("true") for id in test2]
        d=Deferred()
#        d.add_callback(self.cocon)
        d.add_errback(self._handle_query_error)
        
        params={}
        if request.method=="POST":
            data=request.body.readline()
            if data != None or data != '':
                params=json.loads(data,encoding='utf8')
                params=self._stringify_data(params)
        elif request.method=="GET":
            for key in request.GET.keys():         
                if key in self.validGetParams:
                    params[key]=[int(elem) if elem.isdigit()  else elem for elem in request.GET.getall(key) ]
        
        d.start(params)
        return d
#        return params
    
    def _handle_query_error(self,result):
        print("Handling query error",result.exception)
        return self._build_error_response(status=500,resource="environment",errorCode=0,errorMessage="failed to parse query params!")
           
    
    
    
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
import json
import logging
import time

from twisted.internet import reactor, defer
from twisted.web.resource import Resource, NoResource
from twisted.web.server import NOT_DONE_YET
from twisted.python import log,failure
from twisted.python.log import PythonLoggingObserver

from doboz_web.core.server.rest.request_parser import RequestParser
from doboz_web.core.server.rest.response_generator import ResponseGenerator


class BaseRestHandler(Resource):
    isLeaf=False
    def __init__(self,rootUri="http://localhost"):
        Resource.__init__(self)
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
    
    def _build_valid_response_failure(self,result):
        print("error in building valid response",result.exception)
        return self._build_error_response(status=500,resource="environment",errorCode=3,errorMessage="failed to build valid response!")
    
    def result_dict_extractor(self,result={},callback=None):
        """helper function to pass a result as an unpacked dictionary to a function
        """
        return callback(**result)
    
    def _build_resource_uri(self,resourceInstance=None,resourceName=""):
        """
        builds the current resource uri /link, based on resource name and root uri
        """
        self.rootUri=""
        item={}
        item["link"]={}
        item["link"]["rel"]=resourceName
        if resourceInstance:   
            item["link"]["href"]=self.rootUri+str(resourceInstance.id)
            item=dict(item.items() + resourceInstance._toDict().items())
        else:
            item["link"]["href"]=self.rootUri
        print("item",item)
        return item
            
    def _build_resource_list_uri(self,list,resourceName):
        """
        generates a dictionary based data structure for a set of links in json, based on a list
        and a resource name
        """
        result={}
        result[resourceName+"s List"]={}
        result[resourceName+"s List"]["link"]={}
        result[resourceName+"s List"]["link"]["href"]=self.rootUri
        result[resourceName+"s List"]["link"]["rel"]=resourceName+"s"
        result[resourceName+"s List"]["items"]=[self._build_resource_uri(item,resourceName)for item in list] 
        
        return result
    
    def checkAndParseParams(self,request):
        if request.getHeader("Content-Type") not in self.valid_contentTypes:
            self._build_response("", request, 501, "application/json", 0, "unsuported content type for this resource")
        else:
            self._parse_query_params(request)
            
    def _parse_query_params(self,request):
        """
        method parses query params into a dictionary of lists for filter criteria
        """
        #raise Exception("aaah failure in parse params")
        #filterCriteria["active"]=[id.lower() in ("true") for id in test2]
        d=defer.Deferred()
        
        params={}
        if request.method=="POST":
            data=request.content.getvalue()
            if data != None or data != '':
                params=json.loads(data,encoding='utf8')
                params=self._stringify_data(params)
        elif request.method=="GET":
            print("GET params")
            for key in request.args.keys():         
                if key in self.validGetParams:
                    params[key]=[int(elem) if elem.isdigit()  else elem for elem in request.GET.getall(key) ]    
            print(params)
        reactor.callLater(0, d.callback, params)
        return d

    
    def _handle_query_error(self,failure):
        print("Handling query error",str(failure))
        return self._build_error_response(status=500,resource="environment",errorCode=0,errorMessage="failed to parse query params!")
           
    
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
import json
from twisted.internet import reactor, defer
from twisted.python import log,failure
from twisted.web import resource, http
from doboz_web.exceptions import ParameterParseException,UnhandledContentTypeException

class RequestParser(object):
    def __init__(self,request,resource,validContentTypes,validGetParams):
        self.request=request
        self.resource=resource
        self.validContentTypes=validContentTypes
        self.validGetParams=validGetParams
    
   
    def ValidateAndParseParams(self,*args,**kwargs):       
        d=defer.Deferred()     
        d.addCallback(self._validate_params)       
        d.addCallbacks(self._parse_params,errback=self._failure_redirect)
        return d
    
    def _failure_redirect(self,failure,*args,**kwargs):
        return failure
    
    def _validate_params(self,*args,**kwargs):
        """
        method to validate the orginial request/query: checks both for contentype AND for GET requests,
        whether the keys are valid
        """
        if not self.request.getHeader("Content-Type") in self.validContentTypes:
            raise UnhandledContentTypeException()
        if not set(self.request.args.keys()).issubset(set(self.validGetParams)):
            print("TUUT",self.request.args.keys())
            raise ParameterParseException()
        
        return defer.succeed(True)
    
    def _parse_params(self,*args,**kwargs):
        """
        method parses query params into a dictionary of lists for filter criteria
        """
        params={}
        if self.request.method=="POST" or self.request.method=="PUT":
            data=self.request.content.getvalue()
            if data != None or data != '':
                """ In python pre 2.6.5, bug in unicode dict keys"""
                try:
                    params=json.loads(data,encoding='utf8')
                    params=self._stringify_data(params)
                except ValueError:
                    raise ParameterParseException()
        elif self.request.method=="GET":
            def convertElem(elem):
                if elem.isdigit():
                   return int(elem)
                elif elem.lower()=="false":
                    return False
                elif elem.lower()=="true":
                    return True
                else:
                     return elem
            for key in self.request.args.keys():  
                params[key]=[convertElem(elem) for elem in self.request.args[key] ]
            
            try:  
                clientCallback=params.get("callback")   
                self.request.clientCallback=clientCallback[0]
                del params["callback"]
                del params["_"]
                
            except Exception as inst:
                print("ERRRROOOR",inst)
        return defer.succeed( params) 
    
    
    def _stringify_data(self,obj):
        """Convert any dict keys to str, because of a bug in pre 2.6.5 python"""
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
            
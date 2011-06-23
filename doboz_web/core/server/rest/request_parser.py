import json
from twisted.internet import reactor, defer
from twisted.python import log,failure
from twisted.web import resource, http
from doboz_web.core.server.rest.exceptions import ParameterParseException,UnhandledContentTypeException

class RequestParser(object):
    def __init__(self,request,resource,validContentTypes,validGetParams):
        self.request=request
        self.resource=resource
        self.validContentTypes=validContentTypes
        self.validGetParams=validGetParams
    
    @defer.inlineCallbacks
    def ValidateAndParseParams(self):
        if  (yield self._validate_params()):
             defer.returnValue( (yield self._parse_params()))
        else:
            raise UnhandledContentTypeException()
        
    def _validate_params(self):
        """
        method to validate the orginial request/query: checks both for contentype AND for GET requests,
        whether the keys are valid
        """
        d=defer.Deferred()
        if not self.request.getHeader("Content-Type") in self.validContentTypes:
             raise UnhandledContentTypeException()
        if not set(self.request.args.keys()).issubset(set(self.validGetParams)):
            raise ParameterParseException()
        d.callback(self.request.getHeader("Content-Type") in self.validContentTypes and \
        set(self.request.args.keys()).issubset(set(self.validGetParams)))
        return d
        
    def _parse_params(self):
        """
        method parses query params into a dictionary of lists for filter criteria
        """
        d=defer.Deferred()
        params={}
        if self.request.method=="POST":
            data=self.request.content.getvalue()
            if data != None or data != '':
                """ In python pre 2.6.5, bug in unicode dict keys"""
                params=json.loads(data,encoding='utf8')
                params=self._stringify_data(params)
        elif self.request.method=="GET":
            print("GET params")
            for key in self.request.args.keys():         
                    params[key]=[int(elem) if elem.isdigit()  else elem for elem in self.request.args[key] ]    
            print(params)
        d.callback(params)
        return d
    
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
            
from twisted.internet import reactor, defer
from twisted.python import log,failure
from twisted.web import resource, http

import json

class RequestParserDelegate(object):
    def __init__(self,request,resource,validContentTypes):
        self.request=request
        self.resource=resource
        self.validContentTypes=validContentTypes
        self.d=defer.Deferred()
        
    def checkAndParseParams(self):
        self.d.addCallback(self._check_params)
        self.d.addCallbacks(self._parse_params,self._params_check_failed)
        self.d.addErrback(self._params_parse_failed)
        return self.d
    
    def _check_params(self,result):
        if self.request.getHeader("Content-Type") not in self.validContentTypes:
            return failure.Failure()
        else:
            return None
    
    def _parse_params(self,result):
        """
        method parses query params into a dictionary of lists for filter criteria
        """
        #raise Exception("aaah failure in parse params")
        #filterCriteria["active"]=[id.lower() in ("true") for id in test2]
       # raise Exception("aii")
        params={}
        if self.request.method=="POST":
            data=self.request.content.getvalue()
            if data != None or data != '':
                """ In python pre 2.6.5, bug in unicode dict keys"""
                params=json.loads(data,encoding='utf8')
                params=self._stringify_data(params)
        elif request.method=="GET":
            print("GET params")
            for key in self.request.args.keys():         
                if key in self.validGetParams:
                    params[key]=[int(elem) if elem.isdigit()  else elem for elem in self.request.args[key] ]    
            print(params)
       
        return params
    
    
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
            
    def _params_check_failed(self,failure):
        print("param check failed",str(failure))
        return failure
    def _params_parse_failed(self,failure):
        print("parse params failed",str(failure))
        return failure

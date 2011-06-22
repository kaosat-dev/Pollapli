from twisted.internet import reactor, defer
from twisted.python import log,failure
from twisted.web import resource, http

import json

class ResponseGeneratorDelegate(object):
    def __init__(self,request,status=200,contentType="application/json"):
        self.request=request
        self.status=status
        self.contentType=contentType
        
    def wrapAndRespond(self,payload):
        d = defer.Deferred()
        return d
        
    def _build_response(self,payload,errorCode=None,errorMessage=""):
        """
        build a simple response
        """
        print("building response")
        print("params","payload",payload,"request",request,"status",status,"content",contentType,"errocode",errorCode,"errorMessage",errorMessage)
       
        #callback=request.GET.get('callback', '').strip() 
        if isinstance(payload, failure.Failure):
            print("kljlk")
        response=""
        callback=None
        request.setHeader("Content-Type", contentType)
        request.setResponseCode(status)
        #time.sleep(2)
        if isinstance(payload, failure.Failure):
            print("build error")
            response={}
            response["rest_error"]={}
            response["rest_error"]["error_code"]=2#errorCode 
            response["rest_error"]["error_msg"]=payload.getErrorMessage()#;errorMessage
            response["rest_error"]["source"]=self._build_resource_uri(None,self.resource)
        else:
            #raise Exception("lmkmlk")
            payload=payload or ''
            print("building payload",payload)      
            if callback:
                payload= callback+"("+payload+")" 
            response=payload
            
            print("response",response)
        request.write(json.dumps(response))
        request.finish()
import json, sys, traceback,logging
from twisted.internet import reactor, defer
from twisted.python import log,failure
from twisted.web import resource, http
from doboz_web.core.server.rest.exception_converter import ExceptionConverter
from doboz_web.core.server.rest.data_formater import DataFormater
from doboz_web.core.server.rest.data_formater   import JsonFormater


class ResponseGenerator(object):
    def __init__(self,request,status=200,contentType="application/json",resource=None,rootUri=None):
        self.request=request
        self.status=status
        self.contentType=contentType
        self.resource=resource
        self.rootUri=rootUri
        
    def wrapAndRespond(self,payload):
        d = defer.Deferred()
        return d
        
    def _build_response(self,payload,format="json"):
        """
        build a simple response
        """    
        response=""
        callback=getattr(self.request,"clientCallback",None)
        formater=JsonFormater(resource=self.resource)
        
        if isinstance(payload, failure.Failure):
            payload=self._handle_errors(payload)
            self.request.setResponseCode(payload.responseCode)
            self.request.setHeader("Content-Type", "application/pollapli.error+json")
            payload=payload._toDict() or ''
        else:
            self.request.setResponseCode(self.status)
            self.request.setHeader("Content-Type", self.contentType)       
            try:
                payload=formater.format(payload,self.resource,self.rootUri or self.request.path)
            except Exception as inst:
                print("error in reponse gen",str(inst))
                traceback.print_exc(file=sys.stdout)
                payload=""  
            
        if callback:
            payload= callback+"("+payload+")" 
        response=payload or ""
        log.msg("building response using payload:",payload,logLevel=logging.CRITICAL)
        
        self.request.notifyFinish().addErrback(self._responseFailed, self.request._call)
        self._delayedRender(str(response))
       
    def _handle_errors(self,failure):              
        return ExceptionConverter().get_exception(failure.check(*ExceptionConverter().get_exceptionList()))

    def _delayedRender(self,response):
        if not self.request.finished:
            self.request.write(response)
            self.request.finish()
    def _responseFailed(self, err, call):
        call.cancel()
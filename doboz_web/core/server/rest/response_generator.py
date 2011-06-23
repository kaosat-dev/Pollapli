import json
from twisted.internet import reactor, defer
from twisted.python import log,failure
from twisted.web import resource, http
from doboz_web.core.server.rest.exception_converter import ExceptionConverter
from doboz_web.core.server.rest.data_formater import DataFormater


class ResponseGenerator(object):
    def __init__(self,request,status=200,contentType="application/json",exceptionConverter=None,resource=None):
        self.request=request
        self.status=status
        self.contentType=contentType
        self.exceptionConverter=exceptionConverter or ExceptionConverter()
        self.resource=resource
        
    def wrapAndRespond(self,payload):
        d = defer.Deferred()
        return d
        
    def _build_response(self,payload):
        """
        build a simple response
        """
        #callback=request.GET.get('callback', '').strip() 
        response=""
        callback=None
        #    
        if isinstance(payload, failure.Failure):
            payload=self._handle_errors(payload)
            self.request.setResponseCode(payload.responseCode)
            self.request.setHeader("Content-Type", "application/pollapli.error+json")
            payload=payload._toDict() or ''
        else:
            self.request.setResponseCode(self.status)
            self.request.setHeader("Content-Type", self.contentType)   
            
            try:
                payload=payload._toDict() or ''  
                payload=DataFormater(self.resource,self.request.path).format(payload)
            except Exception as inst:
                payload=""     
            
        if callback:
            payload= callback+"("+payload+")" 
        response=payload
        self.request.write(json.dumps(response))
        self.request.finish()
        
    def _handle_errors(self,failure):  
        print(str(failure))
#        exception=failure.check(*self.exceptionConverter.get_exceptionList())
#        if not exception:
            
        return self.exceptionConverter.get_exception(failure.check(*self.exceptionConverter.get_exceptionList()))

    def _format_data(self):
        pass
import logging
import traceback
from doboz_web.core.server.rest.base_rest_handler import BaseRestHandler
from doboz_web.core.server.rest.deferred import Deferred
#from doboz_web.core.tools.twisted_stuff.defer import Deferred

from doboz_web.core.server.bottle import Bottle, request, response 

class EnvsRestHandler(BaseRestHandler):
    def __init__(self,rootUri="http://localhost",environmentManager=None):
        BaseRestHandler.__init__(self,rootUri)
        self.logger=logging.getLogger("dobozweb.core.server.rest.environmentsHandler")
        self.environmentManager=environmentManager
        self.valid_contentTypes.append("application/pollapli.environmentsList+json")   
        self.validGetParams.append('id')
        self.validGetParams.append('status')
        self.resource="environments"
        
    def render_GET(self, request):
        """
        Handler for GET requests of environments
        """
        try:
            d=Deferred()
            d.add_callback(self._parse_query_params)
            d.add_errback(self._handle_query_error)
            d.start(request)
        except Exception as inst:
            print("error",inst)     
            traceback.print_exc()  
        return d.result
    
    def _env_add_failure(self,result):
        print("env add  failure")
        return self._build_error_response(status=500,resource="environment",errorCode=0,errorMessage="failed to add environment!")
        raise Exception("Failed to add environment, breaking chain")
    
    def render_POST(self,request):                   
        def big_fail(failure):
                print("epic fail",failure.exception)
        try:
            d=Deferred()
            d.add_callback(self.dummy_test)
            d.add_callback(self._parse_query_params)
#            d.add_callbacks(callback=self.result_dict_extractor,errback=self._handle_query_error,callbackKeywords={"callback":self.environmentManager.add_environment})    
#            d.add_callbacks(callback=self._build_resource_uri,callbackKeywords={"resourceName":"environment"},errback=self._env_add_failure)
#            d.add_callbacks(callback=self._build_valid_response,callbackKeywords={"request":request,"status":200,"contentType":"text/html"},errback=big_fail)    
            d.start(request)
        except Exception as inst:
            print("error in post",inst)
        print(d.result)
        return d.result
            
    def render_DELETE(self,request):
        d=Deferred()
        d.add_callback(self.environmentManager.clear_environments)
        d.add_errback(self._build_error_response,status=500,resource="environment",errorCode=0,errorMessage="failed to clear environments!")
        d.start()
        return d.result
        
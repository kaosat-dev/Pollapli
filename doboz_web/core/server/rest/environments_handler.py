import logging
from twisted.internet import reactor, defer
from twisted.web.resource import Resource,NoResource
from twisted.web import resource, http
from twisted.python import log,failure
from twisted.python.log import PythonLoggingObserver
from twisted.web.server import NOT_DONE_YET
from twisted.internet.task import deferLater

from doboz_web.core.server.rest.base_rest_handler import BaseRestHandler
from doboz_web.core.server.rest.request_parser import RequestParser
from doboz_web.core.server.rest.response_generator import ResponseGenerator
from doboz_web.core.server.rest.exception_converter import ExceptionConverter
from doboz_web.core.server.rest.exceptions import ParameterParseException,UnhandledContentTypeException
from doboz_web.core.server.rest.environment_handler import EnvironmentHandler
from doboz_web.core.components.environments.exceptions import EnvironmentAlreadyExists

class EnvironmentsHandler(BaseRestHandler):
    """
    Resource in charge of handling the environments (plural) so :
    Adding a new environment
    Listing all environments
    """
    isLeaf=False
    def __init__(self,rootUri="http://localhost",environmentManager=None):
        BaseRestHandler.__init__(self,rootUri)
        self.logger=log.PythonLoggingObserver("dobozweb.core.server.rest.environmentsHandler")
      
        self.environmentManager=environmentManager
        
        self.valid_contentTypes.append("application/pollapli.environmentsList+json")   
        self.validGetParams.append('id')
        self.validGetParams.append('status')
        self.resource="environments"

        self.exceptionConverter=ExceptionConverter()
        self.exceptionConverter.add_exception(ParameterParseException,400 ,1,"Params parse error")
        self.exceptionConverter.add_exception(UnhandledContentTypeException,415 ,2,"bad content type")
        self.exceptionConverter.add_exception(EnvironmentAlreadyExists,409 ,3,"environment already exists")
    
    def getChild(self, id, request):
        try:
            return EnvironmentHandler("http://localhost/environments",self.environmentManager,int(id))    
        except ValueError :
             return self#no id , so return self
    
    def render_POST(self,request):  
        """
        Handler for POST requests of environments
        extract the data from the request body to add a new environment
        """ 
        @defer.inlineCallbacks
        def extract_args(result):
            name=result["name"] or ""
            description=result.get("description") or ""
            status=result.get("status") or "live"
            defer.returnValue((yield self.environmentManager.add_environment(name=name,description=description,status=status)))
             
        r=ResponseGenerator(request,exceptionConverter=self.exceptionConverter,status=201,contentType="application/pollapli.environment+json")
        d=RequestParser(request,"environment",self.valid_contentTypes,self.validGetParams).ValidateAndParseParams()    
        d.addCallbacks(extract_args,errback=r._build_response)    
        d.addBoth(r._build_response)
        return NOT_DONE_YET
    
    def render_GET(self, request):
        """
        Handler for GET requests of environments
        """
        r=ResponseGenerator(request,exceptionConverter=self.exceptionConverter,status=200,contentType="application/pollapli.environmentsList+json")
        d=RequestParser(request,"environment",self.valid_contentTypes,self.validGetParams).ValidateAndParseParams()
        d.addCallbacks(self.environmentManager.get_environments,errback=r._build_response)
        d.addBoth(r._build_response)
        #log.msg("dfsddfdsfs!", logLevel=logging.CRITICAL)
        return NOT_DONE_YET
   
    def render_DELETE(self,request):
        """ 
        Handler for DELETE requests of environments
        WARNING !! needs to be used very carefully, with confirmation on the client side, as it deletes ALL
        environments
        """
        r=ResponseGenerator(request,exceptionConverter=self.exceptionConverter,status=200)
        d= self.environmentManager.clear_environments()
        d.addBoth(r._build_response)
        return NOT_DONE_YET   
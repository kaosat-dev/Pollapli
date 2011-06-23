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


class EnvironmentHandler(BaseRestHandler):
    isLeaf=False
    def __init__(self,rootUri="http://localhost",environmentManager=None,envId=None):
        BaseRestHandler.__init__(self)
        self.rootUri=rootUri
        self.environmentManager=environmentManager
        self.envId=envId
        self.valid_contentTypes.append("application/pollapli.environment+json") 
        
    def render_GET(self, request):
        pass
#        self.logger.info("Using env GET handler")
#        if request.headers.get("Content-Type")=="application/pollapli.envList+json":
#            callback=request.GET.get('callback', '').strip()
#            resp=callback+"()"
#            try:
#                env=self.environmentManager.get_environment(self.envId)
#                lnk='{"link" : {"href":"'+self.rootUri+str(env.id)+'", "rel": "environment"},'
#                resp='{"Environment":'+lnk+env._toJson()+'}}'
#            except Exception as inst:
#                self.logger.critical("environment %s get error %s",str(self.envId), str(inst))
#                abort(404,"environment not found")
#                
#            response.content_type = 'application/json'
#            return resp
#        else:
#            abort(501,"Not Implemented")
#       
    def render_PUT(self,request):
        try:       
            self.environmentManager.add_environment(**self._fetch_jsonData(request))
        except Exception as inst:
            self.logger.critical("error %s",str(inst))
            abort(500,"error in adding environment")
            
    def render_DELETE(self,request):
        try:
            self.environmentManager.remove_environment(self.envId)
        except Exception as inst:
            self.logger.critical("environment deletion error %s",str(inst))
            abort(500,"Failed to delete environments")
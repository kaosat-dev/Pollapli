"""
.. py:module:: files_handler
   :synopsis: rest handler for files interaction.
"""
import logging
from twisted.internet import reactor, defer
from twisted.web.resource import Resource,NoResource
from twisted.web import resource, http
from twisted.python import log,failure
from twisted.python.log import PythonLoggingObserver
from twisted.web.server import NOT_DONE_YET
from twisted.internet.task import deferLater

from doboz_web.core.server.rest.handlers.default_rest_handler import DefaultRestHandler
from doboz_web.core.server.rest.request_parser import RequestParser
from doboz_web.core.server.rest.response_generator import ResponseGenerator


class FilesHandler(DefaultRestHandler):
    """
    Resource in charge of handling the environments (plural) so :
    Adding a new environment
    Listing all environments
    """
    isLeaf=False
    def __init__(self,rootUri="http://localhost"):
        DefaultRestHandler.__init__(self,rootUri)
        self.logger=log.PythonLoggingObserver("dobozweb.core.server.rest.filessHandler")
        
        self.valid_contentTypes.append("application/pollapli.fileList+json")   
        self.validGetParams.append('id')
      
    
    def render_POST(self,request):  
        """
        Handler for POST requests of files
        """ 
#         datafile = request.params["datafile"]
#            self.uploadProgress=0
#            saved_file=open(os.path.join(server.rootPath,"files","machine","printFiles",datafile.filename),'w')
#            saved_file.write(datafile.value)
#            saved_file.close()
#            self.uploadProgress=100
        @defer.inlineCallbacks
        def extract_args(result):
            name=result["name"] or ""
            description=result.get("description") or ""
            status=result.get("status") or "live"
            defer.returnValue((yield self.environmentManager.add_environment(name=name,description=description,status=status)))
             
        r=ResponseGenerator(request,status=201,contentType="application/pollapli.environment+json",resource="environment")
        d=RequestParser(request,"environment",self.valid_contentTypes,self.validGetParams).ValidateAndParseParams()    
        d.addCallbacks(extract_args,errback=r._build_response)    
        d.addBoth(r._build_response)
        return NOT_DONE_YET
    
    def render_GET(self, request):
        """
        Handler for GET requests of files
        """
#         fileList=os.listdir(os.path.join(server.rootPath,"files","machine","printFiles"))
#        try:     
#            finalFileList=map(self.fullPrintFileInfo, fileList)
#            data={"files": finalFileList }
        r=ResponseGenerator(request,status=200,contentType="application/pollapli.environmentsList+json",resource="environments")
        d=RequestParser(request,"environment",self.valid_contentTypes,self.validGetParams).ValidateAndParseParams()
        d.addCallbacks(self.environmentManager.get_environments,errback=r._build_response)
        d.addBoth(r._build_response)
        return NOT_DONE_YET
    
    def render_DELETE(self,request):
        """ 
        Handler for DELETE requests of files
        WARNING !! needs to be used very carefully, with confirmation on the client side, as it deletes ALL
        files
        """
#         fileName=request.params["filename"].strip()
#            filePath=os.path.join(server.rootPath,"files","machine","printFiles",fileName)
#            os.remove(filePath)
#            self.logger.critical("Deleted file: %s",fileName)
        r=ResponseGenerator(request,status=200)
        d= self.environmentManager.clear_environments()
        d.addBoth(r._build_response)
        return NOT_DONE_YET   
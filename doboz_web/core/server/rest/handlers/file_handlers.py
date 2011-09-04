"""
.. py:module:: files_handler
   :synopsis: rest handler for files interaction.
"""
import logging,re,os
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
from doboz_web.core.file_manager import FileManager

class FilesHandler(DefaultRestHandler):
    """
    Resource in charge of handling the uploaded files (plural) so :
    Adding a new file
    Listing all uploaded files
    """
    isLeaf=False
    def __init__(self,rootUri="http://localhost"):
        DefaultRestHandler.__init__(self,rootUri)     
        self.valid_contentTypes.append("application/pollapli.fileList+json")   
        self.valid_contentTypes.append("multipart/form-data")
        self.validGetParams.append('id')
        self.validGetParams.append('datafile')
        
    def getChild(self, id, request):
        try:
            return FileHandler(self.rootUri,id)  
        except ValueError :
             return self
    
    def render_POST(self,request):  
        """
        Handler for POST requests of files
        """ 
        def save_file(result):
            def find_fileName():
                savedPosition = request.content.tell()
                try:
                    request.content.seek(0)
                    request.content.readline()
                    match = re.search(r'filename="([^"]+)"',
                                      request.content.readline())
                    if match:
                        return match.group(1)
                    else:
                        return None
                finally:
                    request.content.seek(savedPosition)
            fileName=find_fileName()
            saved_file=open(os.path.join(FileManager.dataPath,"printFiles",fileName),'w')
            saved_file.write(result.get("datafile")[0])
            saved_file.close()
            
            
        print("POST REQUESt",request,"content",str(request.content))
        r=ResponseGenerator(request,status=201,contentType="application/pollapli.fileList+json",resource="files",rootUri=self.rootUri)
        d=RequestParser(request,"files",self.valid_contentTypes,self.validGetParams).ValidateAndParseParams()      
        d.addCallbacks(callback=save_file,errback=r._build_response)
        d.addBoth(r._build_response)
        request._call=reactor.callLater(0,d.callback,None)
        return NOT_DONE_YET
             
    
    def render_GET(self, request):
        """
        Handler for GET requests of files
        """

        r=ResponseGenerator(request,status=200,contentType="application/pollapli.fileList+json",resource="files",rootUri=self.rootUri)
        d=RequestParser(request,"files",self.valid_contentTypes,self.validGetParams).ValidateAndParseParams()      
        d.addCallbacks(callback=lambda params:FileManager.list_files(),errback=r._build_response)
        d.addBoth(r._build_response)
        request._call=reactor.callLater(0,d.callback,None)
        return NOT_DONE_YET
        
    
    def render_DELETE(self,request):
        """ 
        Handler for DELETE requests of files
        WARNING !! needs to be used very carefully, with confirmation on the client side, as it deletes ALL
        files
        """
        r=ResponseGenerator(request,status=200)
        d=RequestParser(request,"files",self.valid_contentTypes,self.validGetParams).ValidateAndParseParams() 
        d.addCallbacks(callback=lambda params:FileManager.delete_files(),errback=r._build_response) 
        d.addBoth(r._build_response)
        request._call=reactor.callLater(0,d.callback,None)
        return NOT_DONE_YET
    
class FileHandler(DefaultRestHandler):
    """
    Resource in charge of handling a file :
    """
    isLeaf=True
    def __init__(self,rootUri="http://localhost",id=None):
        DefaultRestHandler.__init__(self,rootUri)     
        self.id=id
        self.valid_contentTypes.append("application/pollapli.file+json")   
           
    
    def render_DELETE(self,request):
        """ 
        Handler for DELETE requests of file
        WARNING !! needs to be used very carefully, with confirmation on the client side, as it deletes the file
        """
        r=ResponseGenerator(request,status=200)
        d=RequestParser(request,"files",self.valid_contentTypes,self.validGetParams).ValidateAndParseParams()  
        d.addCallbacks(callback=lambda params:FileManager.delete_file(self.id),errback=r._build_response)
        d.addBoth(r._build_response)
        request._call=reactor.callLater(0,d.callback,None)
        return NOT_DONE_YET

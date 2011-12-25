import os 
import logging,re,os
from twisted.internet import reactor, defer
from twisted.web.resource import Resource,NoResource
from twisted.web import resource, http
from twisted.python import log,failure
from twisted.python.log import PythonLoggingObserver

class PathManager(object):
    
    def __init__(self):
        self.corePath = ""
        
        self.rootPath = ""  
        self.dataPath = ""
        self.uploadPath = ""
        self.tmpPath = ""
        self._addon_path = ""
    
    def list_files(self,path=None):
        result=[]
        for file in os.listdir(self.uploadPath):
            file=os.path.join(self.uploadPath,file)           
         #   print("file:name:",os.path.basename(file) ," size",os.path.getsize(file),"modDate",os.path.getmtime(file),"created",os.path.getctime(file))
            result.append({"name":os.path.basename(file),"size":os.path.getsize(file),"created":os.path.getctime(file),"modified":os.path.getmtime(file)})
        return result
    
    def delete_files(self,path=None):
       # d=defer.Deferred()     
       def _delete_files():
            for file in os.listdir(self.uploadPath):
                filePath=os.path.join(self.uploadPath,file) 
                os.remove(filePath)
            log.msg("FileManager removed all uploaded files sucessfully")
       # d.addCallback(_delete_files)
       # return d
       _delete_files()
    
    def delete_file(self,filename=None):
        #d=defer.Deferred()                 
        def _delete_file(*args,**kwargs):
            filePath=os.path.join(self.uploadPath,filename)
            if os.path.exists(filePath):
                os.remove(filePath)
            log.msg("FileManager removed uploaded file",filename, "sucessfully")

        _delete_file()
       # d.addCallback(_delete_file)
       # return d
        #         fileName=request.params["filename"].strip()
#            filePath=os.path.join(server.rootPath,"files","machine","printFiles",fileName)
#            os.remove(filePath)
#            self.logger.critical("Deleted file: %s",fileName)



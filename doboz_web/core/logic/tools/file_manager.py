import os 
import logging,re,os
from twisted.internet import reactor, defer
from twisted.web.resource import Resource,NoResource
from twisted.web import resource, http
from twisted.python import log,failure
from twisted.python.log import PythonLoggingObserver

class FileManager(object):
    rootDir=None
    corePath=None
    rootPath = None
    @classmethod
    def getRootDir(cls):
        return FileManager.rootDir
    
    @classmethod
    def setRootDir(cls,rootDir):
        FileManager.rootDir=rootDir
        
    @classmethod
    def list_files(cls,path=None):
        result=[]
        for file in os.listdir(cls.uploadPath):
            file=os.path.join(cls.uploadPath,file)           
         #   print("file:name:",os.path.basename(file) ," size",os.path.getsize(file),"modDate",os.path.getmtime(file),"created",os.path.getctime(file))
            result.append({"name":os.path.basename(file),"size":os.path.getsize(file),"created":os.path.getctime(file),"modified":os.path.getmtime(file)})
        return result
    
    @classmethod
    def delete_files(cls,path=None):
       # d=defer.Deferred()     
       def _delete_files():
            
            for file in os.listdir(cls.uploadPath):
                filePath=os.path.join(cls.uploadPath,file) 
                os.remove(filePath)
            log.msg("FileManager removed all uploaded files sucessfully")
       # d.addCallback(_delete_files)
       # return d
       _delete_files()
    
    @classmethod
    def delete_file(cls,filename=None):
        #d=defer.Deferred()     
                
        def _delete_file(*args,**kwargs):
            filePath=os.path.join(cls.uploadPath,filename)
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
    
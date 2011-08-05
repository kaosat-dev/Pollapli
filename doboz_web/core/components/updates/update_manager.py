"""
.. py:module:: addon_manager
   :synopsis: manager of addons : add ons are packages of plugins + extras, and this manager handles the references to all of them
"""
import logging, uuid, pkgutil,zipfile ,os,sys,json
from zipfile import ZipFile
from twisted.internet import reactor, defer
from twisted.python import log,failure
from twisted.python.log import PythonLoggingObserver
from twisted.plugin import getPlugins,IPlugin
from twisted.web import client

from doboz_web.core.components.addons.addon import AddOn
from doboz_web.core.tools.wrapper_list import WrapperList
from doboz_web.core.file_manager import FileManager

class Update(object):
    @classmethod
    def from_dict(self,updateDict):
        """factory method: creates an Update instance from a dict"""
        update=Update()
        for key,value in updateDict.items():
            setattr(update,key,value)   
        return update
    
    def __init__(self,type=None,name=None,description=None,version=None,downloadUrl=None,img=None,tags=None):
        self.type=type
        self.name=name
        self.description=description
        self.version=version
        self.downloadUrl=downloadUrl
        self.img=img
        self.tags=tags
        self.downloaded=False
        self.installed=False
        self.installPath=None
        
    def __str__(self):
        return str(self.__dict__)
    

class UpdateManager(object):
    updates={}

    @classmethod
    def get_updates(cls,category=None):
        downloadUrl="http://kaosat.net/pollapli/"
        updateInfoPath=os.path.join(FileManager.rootDir,"updates.txt") 
        def info_download_complete(result):
            updateFile=file(updateInfoPath,"r")
            updateInfos=json.loads(updateFile.read())
            updateFile.close()
            addOnCount=0
            for update in updateInfos["updates"]:
                 update["downloadUrl"]=downloadUrl+update["downloadUrl"].encode('ascii','ignore')
                 update["img"]=downloadUrl+update["img"].encode('ascii','ignore')
                 newUpdate=Update.from_dict(update)
                 print("new update",str(newUpdate))
                 cls.updates[newUpdate.name]=newUpdate
                 
            return json.dumps(updateInfos)
        def download_failed(failure):
            log.msg("Failed to download update master list: error:",failure.getErrorMessage( ),system="Update",logLevel=logging.CRITICAL)
        
   
        return downloadWithProgress(downloadUrl+"/pollapli_updates.txt",updateInfoPath)\
    .addCallback(info_download_complete).addErrback(download_failed)
    
    @classmethod
    def download_update(cls,name):
        """downloads the specified update"""
        
        def update_download_complete(result,update):
            update.downloaded=True
        
        def update_download_failed(failure,update):
            log.msg("Failed to download update",update.name," error:",failure.getErrorMessage( ),system="Update",logLevel=logging.CRITICAL)
        
        update=cls.updates[name]
        downloadPath=None
        if update.type=="addon":
            downloadPath=os.path.join(cls.addOnPath,update.name)
            update.installPath=downloadPath
        elif update.type=="update":
            pass
        return downloadWithProgress(update.downloadUrl,downloadPath)\
    .addCallback(info_download_complete,update).addErrback(download_failed)
    
    @classmethod
    def install_update(cls,name):
        """installs the specified update"""
        update=cls.updates[name]
        if update.type=="addon":
            pass
        elif update.type=="update":
            pass
             
class Downloader(client.HTTPDownloader):
    def gotHeader(self,headers):
        print("GOT HEADERS")
        self.currentLength=0.0
        if self.status=='200':
            if header.has_key('content-length'):
                self.totalLength=int(headers['content-length'][0])
            else:
                self.totalLength=0
            self.currentLength=0.0
        return client.HTTPDownloader.gotHeader(self,headers)
            
    def pagePart(self, data):
        if not hasattr(self,"currentLength"):
            self.currentLength=0.0
        if not hasattr(self,"totalLength"):
            self.totalLength=0
        
        if self.status == '200':
            
            self.currentLength += len(data)
            if self.totalLength:
                percent = "%i%%" % ((self.currentLength/self.totalLength)*100)
            else:
                percent = '%d K' % (self.currentLength/1000)
            print "Progress: " + percent
        return client.HTTPDownloader.pagePart(self, data)
    
def downloadWithProgress(url, file, contextFactory=None, *args, **kwargs):
        scheme, host, port, path = client._parse(url)
        factory = Downloader(url, file, *args, **kwargs)
        if scheme == 'https':
            from twisted.internet import ssl
            if contextFactory is None:
                contextFactory = ssl.ClientContextFactory( )
                reactor.connectSSL(host, port, factory, contextFactory)
        else:
            reactor.connectTCP(host, port, factory)
        return factory.deferred
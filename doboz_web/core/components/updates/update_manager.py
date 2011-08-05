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

class UpdateManager(object):
    pass

    @classmethod
    def get_updates(cls,category=None):
        downloadUrl="http://kaosat.net/pollapli/"
        updateInfoPath=os.path.join(FileManager.rootDir,"updates.txt") 
        def info_download_complete(result):
             updateFile=file(updateInfoPath,"r")
             updateInfos=json.loads(updateFile.read())
             updateFile.close()
             for addOn in updateInfos["AddOns"]:
                 addOn["file"]=downloadUrl+addOn["file"].encode('ascii','ignore')
                 addOn["img"]=downloadUrl+addOn["img"].encode('ascii','ignore')
             return json.dumps(updateInfos)
        def download_failed(failure):
            print "Error:", failure.getErrorMessage( )
   
        
        return downloadWithProgress(downloadUrl+"/pollapli_updates.txt",updateInfoPath)\
    .addCallback(info_download_complete).addErrback(download_failed)
        
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
import os
from twisted.internet import reactor, defer
from twisted.python import log,failure
from twisted.python.log import PythonLoggingObserver
from twisted.web import client
from pollapli.core.logic.tools.checksum_tools import ChecksumTools


class Downloader(client.HTTPDownloader):
    def __init__(self,url, outfile, headers=None,element=None,*args,**kwargs):
        client.HTTPDownloader.__init__(self, url, outfile, headers=headers ,*args,**kwargs)
        self.currentLength = 0.0  
        self.totalLength = 0
        self.element = element
        self.percent = 0
        
    def gotHeaders(self,headers):
        if self.status=='200':
            if headers.has_key('content-length'):
                self.totalLength=int(headers['content-length'][0])
            else:
                self.totalLength=0   
        return client.HTTPDownloader.gotHeaders(self,headers)
            
    def pagePart(self, data):    
        if self.status == '200':      
            self.currentLength += len(data)
            if self.totalLength:
                self.percent = (self.currentLength/self.totalLength)*100
            else:
                self.percent = self.currentLength/1000
            print("download progress %i %%" % self.percent)
            if self.element is not None:
                self.element.downloadProgress = self.percent 
        return client.HTTPDownloader.pagePart(self, data)
    
class DownloaderWithProgress(object):
    def __init__(self, maxDownloadAttempts=5):
        self._currentDownloads = {}
        self._max_download_attempts = maxDownloadAttempts
        
    @defer.inlineCallbacks
    def download(self,url="", destination="", object=None, refChecksum = None):
        for attempt in range(0,self._max_download_attempts):
            try:
                download = self._createDownloader(url=url, file = destination, element = object)
                self._currentDownloads[url] = download
                yield download.deferred
                if refChecksum is not None:
                    isSameChecksum = yield ChecksumTools.compare_hash(refChecksum, destination) 
                    if not isSameChecksum:
                        raise Exception("File checksum mismatch")
                defer.returnValue(None)
            except Exception as inst:
                print ("Failed to download file at attempt %i because of error %s "%(attempt,str(inst)))
                
        del self._currentDownloads[url]
        if os.path.exists(destination):
            os.remove(destination)
        raise Exception("Failed to download file at %s after %i attempts" %(url, self._max_download_attempts))
        
        
    def _createDownloader(self, url, file, contextFactory=None,element=None, *args, **kwargs):
            scheme, host, port, path = client._parse(url)
            factory = Downloader(url=url, outfile=file, element=element, *args, **kwargs)
            if scheme == 'https':
                if contextFactory is None:
                    try:
                        from twisted.internet import ssl
                        contextFactory = ssl.ClientContextFactory( )
                        reactor.connectSSL(host, port, factory, contextFactory)
                    except Exception as inst:
                        print("failed to create ssl http downloader")
            else:
                reactor.connectTCP(host, port, factory)
            return factory
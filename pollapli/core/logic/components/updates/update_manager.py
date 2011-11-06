"""
.. py:module:: addon_manager
   :synopsis: manager of addons : add ons are packages of plugins + extras, and this manager handles the references to all of them
"""
import logging, uuid, pkgutil,zipfile ,os,sys,json,shutil,time,traceback,ast
from zipfile import ZipFile
from twisted.internet import reactor, defer,task
from twisted.python import log,failure
from twisted.python.log import PythonLoggingObserver
from twisted.plugin import getPlugins,IPlugin
from twisted.web import client

from pollapli.core.logic.tools import checksum_tools
from pollapli.core.logic.tools.path_manager import PathManager
from pollapli.core.logic.tools.signal_system import SignalHander
from pollapli.exceptions import UnknownUpdate, UpdateNotFound
from pollapli.core.logic.components.updates.update import Update

class UpdateManager(object):
    """
    Class for managing updates/addons: works as a container, a handler
    and a central management point for the list of available and installed addons/updates
    """
    def __init__(self, persistenceLayer = None, pathManager = None, updateCheckEnabled=False, updateCheckFrequency = 240):
        self._persistenceLayer = persistenceLayer
        self._pathManager = pathManager
        self.signalChannel = "update_manager"
        self.signalHandler = SignalHander(self.signalChannel)
        self.signalChannelPrefix="update_manager"
        
        self._updates = {}
        self.addons = {}
        
        self._updateCheckFrequency = updateCheckFrequency
        self._updateCheckEnabled = updateCheckEnabled
        self._updateCheck = task.LoopingCall(self.refresh_updateList)
        self._updateListUrl = "http://kaosat.net/pollapli/pollapli_updates.json"
        
        self.addOnPath = "."
        self.updatesPath = "."
        self._maxDownloadAttempts = 5
        self.currentDownloads = {}
        currentInstalls = {}
        
    @defer.inlineCallbacks
    def setup(self):    
        """initial configuration method : 
        * first it checks for locally copied addons and extracts/installs them
        * then tries to fetch the list of available updates from the update server
        * if any new (newer version number or never seen before) update is available, it adds it to the dictionary
        of available updates, but it does NOT download or install those updates
        """      
        updates = yield self._persistenceLayer.load_updates()
        for update in updates:
            self._updates[update.name]=update
        yield self.update_addOns()
        #yield self.refresh_updateList()
        log.msg("Update Manager setup succesfully ",system="Update Manager", logLevel=logging.INFO)
    
    def tearDown(self):
        #TODO: shut down downloader (TCP) cleanly
        pass
       
    def send_signal(self,signal="",data=None):
        prefix = self.signalChannelPrefix+"."
        self.signalHandler.send_message(prefix+signal,self,data) 
        
    def enable_update_checking(self):
        if not self._updateCheckEnabled:
            self._updateCheck.start(interval=self._updateCheckFrequency,now=False)
            self._updateCheckEnabled = True
            
    def disable_update_checking(self):
        if self._updateCheckEnabled:
            self._updateCheck.stop()
            self._updateCheckEnabled = False
        
    """
    ####################################################################################
    The following are the "CRUD" (Create, read, update,delete) methods for the general handling of updates/addons
    """    
    def get_update(self,id=None):
        if id not in self._updates.keys():
            raise UnknownUpdate() 
        return self._updates[id]

    def get_updates(self,filter=None):
        """
        Returns the list of updates, filtered by  the filter param
        the filter is a dictionary of list, with each key beeing an attribute
        to check, and the values in the list , values of that param to check against
        """
        d=defer.Deferred()
        def filter_check(update,filter):
            for key in filter.keys():
                if not getattr(update, key) in filter[key]:
                    return False
            return True
        @defer.inlineCallbacks
        def _get_updates(filter,updateList):
            yield self.refresh_updateList()
            if filter:
                defer.returnValue( [update for update in updateList if filter_check(update,filter)])
            else:               
                defer.returnValue(updateList)
            
        d.addCallback(_get_updates,self.updates.values())
        reactor.callLater(0.5,d.callback,filter)
        return d
        
    def delete_update(self,id):
        """
        Remove an update : this needs a whole set of checks, 
        as it would delete an update completely 
        Params:
        id: the id of the update
        """
        d = defer.Deferred()
        def remove(id,updates):
            update = updates[id]
            if update.type == "update":
                raise Exception("only addons can be removed")
            updates[id].delete()
            del updates[id]
            log.msg("Removed addOn ",update._name,"with id ",id,logLevel=logging.CRITICAL)
        d.addCallback(remove,self._updates)
        reactor.callLater(0,d.callback,id)
        return d
            
    @defer.inlineCallbacks
    def clear_updates(self):
        """
        Removes & deletes ALL the updates that are addons "simple" updates cannot be deleted
        This should be used with care,as well as checks on client side
        """
        for updateId in self._updates.iterkeys():
            yield self.delete_update(id = updateId)        
   
   
    """
    ####################################################################################
    Update download and installation methods   
    """
    def refresh_updateList(self,category=None):
        """Fetches the remote update list, downloads it, and if there were any changes, updates
        the in memory update list accordingly
        TODO: add last change date checking to file
        """
        log.msg("checking for new updates : time",time.time(),logLevel=logging.CRITICAL)
        updateInfoPath=os.path.join(self._pathManager.tmpPath,"updates.txt") 
        
        def info_download_complete(result):
            self._parse_update_file()
        
        def download_failed(failure):
            log.msg("Failed to download update master list: error:",failure.getErrorMessage( ),system="Update Manager",logLevel=logging.CRITICAL)
        
        return downloadWithProgress(self._updateListUrl,updateInfoPath)\
    .addCallback(info_download_complete).addErrback(download_failed)
    
    def setup_update(self,name):
        #for id, val in enumerate(ints):
        for attempt in range(0,self._maxDownloadAttempts):          
            try:
                yield self._downloadUpdate()
                yield self._installUpdate()
            except :pass
        #self.download_update(name).addCallback(self.install_update,name)
    
    @defer.inlineCallbacks
    def _download_update(self, id):
        """downloads the specified update, if the download was successfull, it checks the update's md5 checksum
        versus the one stored in the update info for integretiy, and if succefull, dispatches a success message
        """
        if not id in self._updates.keys():
            raise UpdateNotFound()
        update = self._updates[id]
        for attempt in range(0,self._maxDownloadAttempts):  
            try :
                downloadPath = os.path.join(self._pathManager.tmpPath,update.file) 
                yield  self._download_file(url = update.downloadUrl, downloadPath = downloadPath)
                defer.returnValue(True)
            except:pass
        raise Exception("Failed to download update", update.name,"after",self._maxDownloadAttempts)
#    
#    def update_download_succeeded(result,update):
#            if update.id in self.currentDownloads:
#                del self.currentDownloads[update.id]
#            #remove the current update's downloader from the dict of current downloads
#            update.downloaded=True
#            update.save()
#            self.send_signal("update_download_succeeded", update)
#            log.msg("Successfully downloaded update ",update.name,system="Update Manager",logLevel=logging.DEBUG)
#            
#        def update_download_failed(failure,update,downloadAttempts):
#            del self.currentDownloads[update.id]#remove the current update's downloader from the dict of current downloads
#            downloadAttempts+=1
#            log.msg("Failed to download update or checksum error",update.name," error:",failure.getErrorMessage(),"attempt",downloadAttempts,system="Update Manager",logLevel=logging.CRITICAL)
#            
#            if downloadAttempts>=self.maxDownloadAttempts:
#                self.send_signal("update_download_failed", update)
#                log.msg("Failed to download update or checksum error after all attemps",update.name," error:",failure.getErrorMessage(),system="Update Manager",logLevel=logging.CRITICAL)
#            
#            else:
#                return self._download_file(url=update.downloadUrl, file=downloadPath,element=update)\
#            .addCallback(checksum_tools.compare_hash,update.fileHash,downloadPath).addCallbacks(callback=update_download_succeeded,callbackArgs=[update],errback=update_download_failed,errbackArgs=[update,downloadAttempts])#.addErrback(update_download_failed,update)
#   
##               return downloadWithProgress(update.downloadUrl,downloadPath)\
##    .addCallback(checksum_tools.compare_hash,update.fileHash,downloadPath).addCallbacks(callback=update_download_succeeded,callbackArgs=[update],errback=update_download_failed,errbackArgs=[update,downloadAttempts])
##        
#        update=self.updates.get(name)
#        if update==None:
#            raise UnknownUpdate()
#        update=self.updates[name]
#        downloadAttempts=0
#        downloadPath=None
#        if update.type=="addon":
#            downloadPath=os.path.join(self.updatesPath,update.file)
#            update.installPath=self.addOnPath
#        elif update.type=="update":
#            pass
#        return self._download_file(url=update.downloadUrl, file=downloadPath,element=update)\
#    .addCallback(checksum_tools.compare_hash,update.fileHash,downloadPath).addCallbacks(callback=update_download_succeeded,callbackArgs=[update],errback=update_download_failed,errbackArgs=[update,downloadAttempts])#.addErrback(update_download_failed,update)
#         
    
    
    def  _install_update(self,id):
        """installs the specified update"""
#        def install_succeeded(result,update):
#            del self.currentDownloads[update.id]
#            update.installed=True
#            if os.path.exists(originalFilePath):
#                os.remove(originalFilePath)
#            self.send_signal("update_install_succeeded", update)
#            log.msg("Successfully installed update ",update.name,system="Update Manager",logLevel=logging.DEBUG)
#            return True
#        
#        def install_failed(failure,update,*args,**kwargs):
#            del self.currentDownloads[update.id]
#            self.send_signal("update_install_failed", update)
#            log.msg("Failed to install update",update.name," error:",failure.getErrorMessage(),system="Update Manager",logLevel=logging.CRITICAL)      
#            return False
            
        update = self._updates[id]
        if not update.downloaded:
            raise Exception("Cannot install update that was not downloaded first")
        
        tmpUpdatePath = ""
        if update.type == "addon":
                destinationPath = ""
                shutil.copy2(tmpUpdatePath, os.path.join(self.addOnPath,update.file))
                update.installPath = self.addOnPath
                yield self.update_addOns().addCallbacks(callback=install_succeeded,callbackArgs=[update],errback=install_failed,errbackArgs=[update])
        elif update.type == "update":
                #TODO: add backuping of original files
                #TODO: add restart of system 
                destinationPath = ""
                shutil.copy2(tmpUpdatePath, os.path.join(self.addOnPath,update.file))
                update.installPath = "."
      
    """
    ####################################################################################
    Add on specific Methods    
    """
    def extract_addons(self):
        """
        helper "hack" function to extract egg/zip files into their adapted directories
        """
        d=defer.Deferred()      
        def extract(addOnPath):
            dirs=os.listdir(addOnPath)
            for dir in dirs:
                baseName,ext= os.path.splitext(dir)
                baseName=baseName.replace('-','_')
                baseName=baseName.replace('.','_') 
                if ext==".egg" or ext==".zip":
                    eggFilePath=os.path.join(addOnPath,dir)
                    eggfile=ZipFile(eggFilePath, 'r')
                    eggfile.extractall(path=os.path.join(addOnPath,baseName))
                    eggfile.close()
                    os.remove(eggFilePath)
        d.addCallback(extract)
        reactor.callLater(1,d.callback,self.addOnPath)
        return d
    
    def list_addons(self):
        """
        Scans the addOns' path for addons , and adds them to the list of currently available addOns
        """
        d=defer.Deferred()   
        def scan(addOnList,addOnPath,*args,**kwargs):
            dirs=os.listdir(addOnPath)
            index=0
            for dir in dirs:
                fullpath=os.path.join(addOnPath,dir)           
                if os.path.isdir(fullpath):
                    if not fullpath in sys.path:
                        sys.path.insert(0, fullpath) 
                    addOnList[index]=Update(type="addon",name=dir,description="",installPath=fullpath,enabled=True) 
                    index+=1
            log.msg("Listed addons: ",[str(addon) for addon in addOnList.itervalues()],system="Update Manager",logLevel=logging.DEBUG)
            
        d.addCallback(scan,self.addOnPath)
        reactor.callLater(1,d.callback,self.addons)
        return d  
    
    @defer.inlineCallbacks
    def update_addOns(self):
        """
        wrapper method, for extraction+ list update in case of newly installed addons
        """
        yield self.extract_addons()
        yield self.list_addons()
        
    @defer.inlineCallbacks
    def get_plugins(self,interface=None,addOnName=None):
        """
        find a specific plugin in the list of available addOns, by interface and/or addOn
        """
        plugins=[]
        @defer.inlineCallbacks
        def scan(path):
            plugins=[]
            try:
                addonpackages=pkgutil.walk_packages(path=[path], prefix='')
                for loader,name,isPkg in addonpackages: 
                    mod = pkgutil.get_loader(name).load_module(name)           
                    try:
                        plugins.extend((yield getPlugins(interface,mod)))
                    except Exception as inst:
                        log.msg("error in fetching plugin: ",str(inst),system="Update Manager",logLevel=logging.CRITICAL)
            except Exception as inst:
                log.msg("error2 in fetching plugin: ",str(inst),system="Update Manager",logLevel=logging.CRITICAL)
            defer.returnValue(plugins)
        
        
        for addOn in self.addons.itervalues():
            if addOnName:
                if addOn.name==addOnName and addOn.enabled:
                    plugins.extend((yield scan(addOn.installPath)))
            else:
                if  addOn.enabled:
                    plugins.extend((yield scan(addOn.installPath)))
        log.msg("Got plugins: ",str(plugins),system="Update Manager",logLevel=logging.DEBUG)
        defer.returnValue(plugins)
        
    def set_addon_state(self,id=None,name=None,activate=False):
        d=defer.Deferred()
        def activate(addOns):
            if id:
                addOns[id].enabled = activate
            elif name:
                for addOn in addOns.itervalues():
                    if addOn.name==name:
                        addOn.enabled = activate
                    
        d.addCallback(activate)
        reactor.callLater(0.2,d.callback,self.addons)
        return d
            
    """
    ####################################################################################
    Helper Methods    
    """
    def _parse_update_file(self):
        updatesFileName = os.path.join(self._pathManager.tmpPath,"pollapli_updates.json")
        updateFile = file(updatesFileName,"r")
        updateInfos = json.loads(updateFile.read(),"iso-8859-1")    
        updateFile.close()

        updateList = [Update.from_dict(update) for update in updateInfos["updates"]]   
        addedUpdates = []
        updatedUpdates  = []
        
        for update in updateList:
            if update._id in self._updates.keys():
                if update > self._updates[update._id] and self._updates[update._id].installed == True:
                    updatedUpdates.append(update)
                    #addedUpdates.append(update)
            else:
                addedUpdates.append(update)
        
        for update in addedUpdates:
            self._updates[update._id] = update
            
        if len(addedUpdates)>0:
            self.send_signal("new_updates_available", addedUpdates)   
    
    def _download_file(self,url, file, contextFactory=None,element=None, *args, **kwargs):    
        scheme, host, port, path = client._parse(url)
        factory = Downloader(url=url, outfile=file,signalSender=self.send_signal,element=element)
        if scheme == 'https':
            from twisted.internet import ssl
            if contextFactory is None:
                contextFactory = ssl.ClientContextFactory( )
                reactor.connectSSL(host, port, factory, contextFactory)
        else:
            reactor.connectTCP(host, port, factory)
        self.currentDownloads[element.id]=factory
        return factory.deferred
   
    
    
             
class Downloader(client.HTTPDownloader):
    
    def __init__(self,url, outfile, headers=None, signalSender=None,element=None,*args,**kwargs):
        client.HTTPDownloader.__init__(self, url, outfile, headers=headers ,*args,**kwargs)
        self.signalSender=signalSender
        self.currentLength=0.0  
        self.totalLength=0
        self.element=element
        
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
                percent = "%i%%" % ((self.currentLength/self.totalLength)*100)
            else:
                percent = '%d K' % (self.currentLength/1000)
            if self.signalSender is not None:
                #hack
                self.element.send_signal("download_updated",{"progress" : self.currentLength/self.totalLength})
                #self.signalSender("update."+str(self.element.id)+".download_updated",{"progress: " : self.currentLength/self.totalLength})
           # print "Progress: " + percent
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
    
    
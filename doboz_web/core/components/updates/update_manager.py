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
from twistar.registry import Registry
from twistar.dbobject import DBObject
from twistar.dbconfig.base import InteractionBase

from doboz_web.exceptions import UnknownUpdate
from doboz_web.core.tools.wrapper_list import WrapperList
from doboz_web.core.file_manager import FileManager
from doboz_web.core.signal_system import SignalHander
from doboz_web.core.tools import checksum_tools


class Update(DBObject):
    EXPOSE=["id","name","description","type","version","img","tags","downloaded","enabled","installed"]
    
    """update class: for all type of updates (standard update or addon)
    Contains all needed info for handling of updates"""
    
    @classmethod
    def from_dict(self,updateDict):
        """factory method: creates an Update instance from a dict"""
        update=Update()
        for key,value in updateDict.items():
            setattr(update,key,value)  
        return update
    
    def __init__(self,type=None,name=None,description=None,version=None,downloadUrl=None,img=None,tags=None,installPath=None,enabled=False,file=None,fileHash=None,*args,**kwargs):
        DBObject.__init__(self,**kwargs)
        self.type=type
        self.name=name

        self.description=description 
        self.version=version
        self.downloadUrl=downloadUrl
        self.img=img
        self.tags=tags
        self.file=file
        self.fileHash=fileHash
        self.downloaded=False
        self.enabled=enabled
        self.installed=False
        self.installPath=installPath
        
        self.parentManager=None
        
    def setup(self):
        pass
       # self.signalChannelPrefix=str(self.id)
    
    def send_signal(self,signal="",data=None):
        self.parentManager.send_signal("update_"+str(self.id)+"."+signal,data)
       
        
    def afterInit(self):  
        self.tags=ast.literal_eval(self.tags)
        self.downloadUrl=str(self.downloadUrl)
        
      
        
    def beforeSave(self):  
#        if self.description is not None:
#            self.description= self.description.encode('latin-1').decode('utf-8') 
       
        pass
        
    def __str__(self):
        return str(self.__dict__)
   

class UpdateManager(object):
    """
    Class for managing updates/addons: works as a container, a handler
    and a central management point for the list of available and installed addons/updates
    """
    updates={}
    addons={}
    addOnPath=None
    updatesPath=None
    maxDownloadAttempts=5
    currentDownloads={}
    currentInstalls={}
    
    signalChannel="update_manager"
    signalHandler=SignalHander(signalChannel)
    
    @classmethod
    @defer.inlineCallbacks
    def setup(cls):    
        """initial configuration method : 
        * first it checks for locally copied addons and extracts/installs them
        * then tries to fetch the list of available updates from the update server
        * if any new (newer version number or never seen before) update is available, it adds it to the dictionary
        of available updates, but it does NOT download or install those updates
        """      
        cls.signalChannelPrefix="update_manager"
        
        def _loadAllUpdates(result):
            for update in result:
                update.parentManager=cls
                cls.updates[update.name]=update
                
            
        Update.all().addCallback(_loadAllUpdates)
        yield cls.update_addOns()
        yield cls.refresh_updateList()
        
        """just for testing"""
#        yield cls.download_update("Virtual device add on")
#        yield cls.install_update("Virtual device add on")
#        yield cls.download_update("Arduino Example")
#        yield cls.install_update("Arduino Example")
        
        cls.updateCheck= task.LoopingCall(cls.refresh_updateList)
        cls.updateCheck.start(interval=240,now=False)
        log.msg("Update Manager setup succesfully ",system="Update Manager")
        defer.returnValue(None)
    @classmethod     
    def send_signal(cls,signal="",data=None):
        prefix=cls.signalChannelPrefix+"."
        cls.signalHandler.send_message(prefix+signal,cls,data) 
    """
    ####################################################################################
    The following are the "CRUD" (Create, read, update,delete) methods for the general handling of updates/addons
    """
    @defer.inlineCallbacks
    def add_addOn(self,name="addOn",description="",type=None,connector=None,driver=None,*args,**kwargs):
        """
        Add a new addOn to the list of addOns of the current environment
        Params:
        name: the name of the addOn
        Desciption: short description of addOn
        type: the type of the addOn : very important , as it will be used to instanciate the correct class
        instance
        Connector:the connector to use for this addOn
        Driver: the driver to use for this addOn's connector
        """
    
        defer.returnValue(None)
    
    def get_addOns(self,filter=None):
        """
        Returns the list of addOns, filtered by  the filter param
        the filter is a dictionary of list, with each key beeing an attribute
        to check, and the values in the list , values of that param to check against
        """
        d=defer.Deferred()
        
        def filter_check(addOn,filter):
            for key in filter.keys():
                if not getattr(addOn, key) in filter[key]:
                    return False
            return True
      
        def get(filter,addOnsList):
            if filter:
                return WrapperList(data=[addOn for addOn in addOnsList if filter_check(addOn,filter)],rootType="addOns")
            else:               
                return WrapperList(data=addOnsList,rootType="addOns")
            
        d.addCallback(get,self.addOns.values())
        reactor.callLater(0.5,d.callback,filter)
        return d
    
    @classmethod
    def get_update(cls,id=None,name=None):
        update=None
        if name is not None:
            update= cls.updates.get(name)
            
        elif id is not None:
            update =[updt for updt in cls.updates.itervalues() if updt.id==id  ][0]

        if update is not None:
            return update
        else:
            raise UnknownUpdate()   
    
    @classmethod
    def get_updates(cls,filter=None):
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
            yield cls.refresh_updateList()
            if filter:
                defer.returnValue( WrapperList(data=[update for update in updateList if filter_check(update,filter)],rootType="updates"))
            else:               
                defer.returnValue( WrapperList(data=updateList,rootType="updates"))
            
        d.addCallback(_get_updates,cls.updates.values())
        reactor.callLater(0.5,d.callback,filter)
        return d
    
    def get_addOn(self,id):
        if not id in self.addOns.keys():
            raise AddOnNotFound()
        return self.addOns[id]
    
    def update_addOn(self,id,name,description):
        """Method for addOn update"""
        return self.addons[id]
        #self.addOns[id].update()
    
    def delete_addOn(self,id):
        """
        Remove an addOn : this needs a whole set of checks, 
        as it would delete an addOn completely 
        Params:
        id: the id of the addOn
        """
        d=defer.Deferred()
        def remove(id,addOns):
            addOnName=addOns[id].name
            addOns[id].delete()
            del addOns[id]
            log.msg("Removed addOn ",addOnName,"with id ",id,logLevel=logging.CRITICAL)
        d.addCallback(remove,self.addOns)
        reactor.callLater(0,d.callback,id)
        return d
            
    @defer.inlineCallbacks
    def clear_addons(self):
        """
        Removes & deletes ALL the addons, should be used with care,as well as checks on client side
        """
        for addOns in self.addons.values():
            yield self.delete_addOn(addOn.id)        
        defer.returnValue(None)
   
    """
    ####################################################################################
    Helper Methods    
    """
    @classmethod
    def _download_file(cls,url, file, contextFactory=None,element=None, *args, **kwargs):    
        scheme, host, port, path = client._parse(url)
        factory = Downloader(url=url, outfile=file,signalSender=cls.send_signal,element=element)
        if scheme == 'https':
            from twisted.internet import ssl
            if contextFactory is None:
                contextFactory = ssl.ClientContextFactory( )
                reactor.connectSSL(host, port, factory, contextFactory)
        else:
            reactor.connectTCP(host, port, factory)
            
        cls.currentDownloads[element.id]=factory
        return factory.deferred
   
        
    
    
   
    
    @classmethod 
    def refresh_updateList(cls,category=None):
        """Fetches the remote update list, downloads it, and if there were any changes, updates
        the in memory update list accordingly
        TODO: add last change date checking to file
        """
        log.msg("checking for new updates : time",time.time(),logLevel=logging.CRITICAL)
        
        downloadUrl="http://kaosat.net/pollapli/"
        updateInfoPath=os.path.join(cls.updatesPath,"updates.txt") 
        def mycmp(a, b):
            from pkg_resources import parse_version as V
            return cmp(V(a),V(b))
         
        
        def info_download_complete(result):
            updateFile=file(updateInfoPath,"r")
            updateInfos=json.loads(updateFile.read(),"iso-8859-1")
            
            updateFile.close()
            addOnCount=0
            
            foundUpdates=updateInfos["updates"]  
            newUpdates=[]
            updates={}
    
            for update in foundUpdates:
                update["downloadUrl"]=downloadUrl+update["file"].encode('ascii','ignore')
                update["img"]=downloadUrl+update["img"].encode('ascii','ignore')
                newUpdate=Update.from_dict(update)
                updates[newUpdate.name]=newUpdate
            
            """we do a old vs new dif"""
            olds=set(cls.updates.keys())
            news=set(updates.keys())
            addedUpdates=list(news-olds)
            removedUpdates=list(olds-news)
            
            """remove not used, and no more valid updates"""
            for updateName in removedUpdates:
                update=cls.updates[updateName]
                if not update.installed and not update.downloaded:
                    del cls.updates[update.name]
            
            for updateName in updates:       
                oldUpdate=cls.updates.get(updateName)    
                newUpdate=updates.get(updateName)
                addUpdate=True
                if oldUpdate is not None:
                    if mycmp(oldUpdate.version,newUpdate.version)>=0:                        
                        addUpdate=False
                if addUpdate:
                    newUpdate.save()
                    newUpdate.parentManager=cls
                    cls.updates[updateName]=newUpdate
                    
                    newUpdates.append(newUpdate)
                

            if len(newUpdates)>0:
                cls.send_signal("new_updates_available", newUpdates)
        
        def download_failed(failure):
            log.msg("Failed to download update master list: error:",failure.getErrorMessage( ),system="Update Manager",logLevel=logging.CRITICAL)
        
   
        return downloadWithProgress(downloadUrl+"/pollapli_updates.txt",updateInfoPath)\
    .addCallback(info_download_complete).addErrback(download_failed)
    
    @classmethod
    def download_update(cls,name):
        """downloads the specified update, if the download was successfull, it checks the update's md5 checksum
        versus the one stored in the update info for integretiy, and if succefull, dispatches a success message
        """
        def update_download_succeeded(result,update):
            if update.id in cls.currentDownloads:
                del cls.currentDownloads[update.id]
            #remove the current update's downloader from the dict of current downloads
            update.downloaded=True
            update.save()
            cls.send_signal("update_download_succeeded", update)
            log.msg("Successfully downloaded update ",update.name,system="Update Manager",logLevel=logging.DEBUG)
            
        def update_download_failed(failure,update,downloadAttempts):
            del cls.currentDownloads[update.id]#remove the current update's downloader from the dict of current downloads
            downloadAttempts+=1
            log.msg("Failed to download update or checksum error",update.name," error:",failure.getErrorMessage(),"attempt",downloadAttempts,system="Update Manager",logLevel=logging.CRITICAL)
            
            if downloadAttempts>=cls.maxDownloadAttempts:
                cls.send_signal("update_download_failed", update)
                log.msg("Failed to download update or checksum error after all attemps",update.name," error:",failure.getErrorMessage(),system="Update Manager",logLevel=logging.CRITICAL)
            
            else:
                return cls._download_file(url=update.downloadUrl, file=downloadPath,element=update)\
            .addCallback(checksum_tools.compare_hash,update.fileHash,downloadPath).addCallbacks(callback=update_download_succeeded,callbackArgs=[update],errback=update_download_failed,errbackArgs=[update,downloadAttempts])#.addErrback(update_download_failed,update)
   
#               return downloadWithProgress(update.downloadUrl,downloadPath)\
#    .addCallback(checksum_tools.compare_hash,update.fileHash,downloadPath).addCallbacks(callback=update_download_succeeded,callbackArgs=[update],errback=update_download_failed,errbackArgs=[update,downloadAttempts])
#        
        update=cls.updates.get(name)
        if update==None:
            raise UnknownUpdate()
        update=cls.updates[name]
        downloadAttempts=0
        downloadPath=None
        if update.type=="addon":
            downloadPath=os.path.join(cls.updatesPath,update.file)
            update.installPath=cls.addOnPath
        elif update.type=="update":
            pass
        return cls._download_file(url=update.downloadUrl, file=downloadPath,element=update)\
    .addCallback(checksum_tools.compare_hash,update.fileHash,downloadPath).addCallbacks(callback=update_download_succeeded,callbackArgs=[update],errback=update_download_failed,errbackArgs=[update,downloadAttempts])#.addErrback(update_download_failed,update)
     
    @classmethod
    @defer.inlineCallbacks
    def install_update(cls,name):
        """installs the specified update"""
        def install_succeeded(result,update):
            del cls.currentDownloads[update.id]
            update.installed=True
            if os.path.exists(originalFilePath):
                os.remove(originalFilePath)
            cls.send_signal("update_install_succeeded", update)
            log.msg("Successfully installed update ",update.name,system="Update Manager",logLevel=logging.DEBUG)
            return True
        
        def install_failed(failure,update,*args,**kwargs):
            del cls.currentDownloads[update.id]
            cls.send_signal("update_install_failed", update)
            log.msg("Failed to install update",update.name," error:",failure.getErrorMessage(),system="Update Manager",logLevel=logging.CRITICAL)      
            return False
            
        update=cls.updates[name]
        
        if update.downloaded:
            originalFilePath=os.path.join(cls.updatesPath,update.file)
            cls.currentDownloads[update.id]=update
            if update.type=="addon":
                shutil.copy2(originalFilePath, os.path.join(cls.addOnPath,update.file))
                update.installPath=cls.addOnPath
                
                yield cls.update_addOns().addCallbacks(callback=install_succeeded,callbackArgs=[update],errback=install_failed,errbackArgs=[update])
            elif update.type=="update":
                pass
       
    
    @classmethod
    def downloadAndInstall_update(cls,name):
        cls.download_update(name).addCallback(cls.install_update,name)

    @classmethod
    def extract_addons(cls):
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
        reactor.callLater(1,d.callback,cls.addOnPath)
        return d
    
    @classmethod
    def list_addons(cls):
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
            
        d.addCallback(scan,cls.addOnPath)
        reactor.callLater(1,d.callback,cls.addons)
        return d  
    
    @classmethod
    @defer.inlineCallbacks
    def update_addOns(cls):
        """
        wrapper method, for extraction+ list update in case of newly installed addons
        """
        yield cls.extract_addons()
        yield cls.list_addons()
        defer.returnValue(None)
        
    @classmethod
    @defer.inlineCallbacks
    def get_plugins(cls,interface=None,addOnName=None):
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
        
 
        for addOn in cls.addons.itervalues():
            if addOnName:
                if addOn.name==addOnName and addOn.enabled:
                    plugins.extend((yield scan(addOn.installPath)))
            else:
                if  addOn.enabled:
                    plugins.extend((yield scan(addOn.installPath)))
        log.msg("Got plugins: ",str(plugins),system="Update Manager",logLevel=logging.DEBUG)
        defer.returnValue(plugins)
        
    @classmethod
    def set_addon_state(cls,id=None,name=None,activate=False):
        d=defer.Deferred()
        def activate(addOns):
            if id:
                addOns[id].enabled=activate
            elif name:
                for addOn in addOns.itervalues():
                    if addOn.name==name:
                        addOn.enabled=activate
                    
        d.addCallback(activate)
        reactor.callLater(0.2,d.callback,cls.addons)
        return d
    
    
             
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
    
    
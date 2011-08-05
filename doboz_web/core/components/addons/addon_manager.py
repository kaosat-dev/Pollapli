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


from doboz_web.core.components.addons.addon import AddOn
from doboz_web.core.tools.wrapper_list import WrapperList
from doboz_web.core.file_manager import FileManager
#from doboz_web.exceptions import UnknownaddOnType,addOnNotFound


class AddOnManager(object):
    """
    Class for managing addons: works as a container, a handler
    and a central managment point for the list of avalailable addons
    """
    addons={}
    addOnPath=None
    #downloader=Downloader()
    
    def __init__(self):
        self.logger=log.PythonLoggingObserver("dobozweb.core.components.addOns.addonManager")
    
    @classmethod
    @defer.inlineCallbacks
    def setup(cls):          
        #yield cls.download_addons()
        yield cls.update_addOns()
        log.msg("AddOn Manager setup succesfully ",system="AddOn Manager")
        
        defer.returnValue(None)
    """
    ####################################################################################
    The following are the "CRUD" (Create, read, update,delete) methods for the general handling of addOns
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
    def download_addon(cls,url):
        pass
    @classmethod
    def download_addons(cls):
        updateInfoPath=os.path.join(FileManager.rootDir,"updates.txt") 
        def addon_download_complete(result):
            print("add on downloaded succefully")
        @defer.inlineCallbacks
        def info_download_complete(result):
             print "Progress: 100 Download Complete. "
             jsonstuff=file(updateInfoPath,"r")
             updateInfos=json.loads(jsonstuff.read())
             jsonstuff.close()
             print("Loaded update json:",updateInfos)
             print("Addons found",updateInfos["AddOns"])
             print("Addon Path",updateInfos["AddOns"][0]["file"])
             for addOn in updateInfos["AddOns"]:
                 addOnFile=addOn["file"].encode('ascii','ignore')
                 yield downloadWithProgress("http://kaosat.net/pollapli/"+addOnFile,os.path.join(cls.addOnPath,addOnFile))\
                 .addCallback(addon_download_complete).addErrback(download_failed)
                 
             yield cls.update_addOns()
        def download_failed(failure):
            print "Error:", failure.getErrorMessage( )
   
        
        return downloadWithProgress("http://kaosat.net/pollapli/pollapli_updates.txt",updateInfoPath)\
    .addCallback(info_download_complete).addErrback(download_failed)
       # return downloadWithProgress("http://www.kaosat.net/index.html","kpouer.html").addCallback(downloadComplete).addErrback(downloadError)
    
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
        reactor.callLater(1,d.callback,AddOnManager.addOnPath)
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
                        #print("adding ",fullpath,"to sys path")
                        sys.path.insert(0, fullpath) 
                    addOnList[index]=AddOn(name=dir,description="",path=fullpath) 
                    index+=1
            
        d.addCallback(scan,AddOnManager.addOnPath)
        reactor.callLater(1,d.callback,AddOnManager.addons)
        return d  
    
    @classmethod
    @defer.inlineCallbacks
    def update_addOns(cls):
        """
        wrapper method, for extraction+ list update in case of newly installed addons
        """
        yield AddOnManager.extract_addons()
        yield AddOnManager.list_addons()
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
                        print("error in fetching plugin: %s"%str(inst))
            except Exception as inst:
                print("error2 in fetching plugin: %s"%str(inst))
            defer.returnValue(plugins)
        
 
        for addOn in AddOnManager.addons.itervalues():
            if addOnName:
                if addOn.name==addOnName and addOn.enabled:
                    plugins.extend((yield scan(addOn.path)))
            else:
                if  addOn.enabled:
                    plugins.extend((yield scan(addOn.path)))
                
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
        reactor.callLater(2,d.callback,AddOnManager.addons)
        return d

from twisted.web import client
   
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
    


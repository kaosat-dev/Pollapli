"""
.. py:module:: addon_manager
   :synopsis: manager of addons : add ons are packages of plugins + extras, and this manager handles the references to all of them
"""
import logging
import uuid
import pkgutil
import zipfile 
from zipfile import ZipFile
import os
import sys
from twisted.internet import reactor, defer
from twisted.enterprise import adbapi
from twistar.registry import Registry
from twistar.dbobject import DBObject
from twistar.dbconfig.base import InteractionBase
from twisted.python import log,failure
from twisted.python.log import PythonLoggingObserver
from twisted.plugin import getPlugins,IPlugin


from doboz_web.core.components.addons.addon import AddOn
from doboz_web.core.tools.wrapper_list import WrapperList
from doboz_web.exceptions import UnknownNodeType,NodeNotFound


class AddOnManager(object):
    """
    Class for managing addons: works as a container, a handler
    and a central managment point for the list of avalailable addons
    """
    addons={}
    addOnPath=None
    def __init__(self):
        self.logger=log.PythonLoggingObserver("dobozweb.core.components.nodes.addonManager")
        
    @defer.inlineCallbacks    
    def setup(self):
        def addAddOn(nodes,nodeTypes):
            for node in nodes:
                node.environment.set(self.parentEnv)
                self.nodes[node.id]=node
                node.setup()
                for capability in nodeTypes.values():            
                    def addCapabilities(caps,node):
                        if len(caps)>0:
                            node.capability=caps[0] 
                    capability.find(where=['node_id = ?', node.id]).addCallback(addCapabilities,node)
                
                
        yield Node.all().addCallback(addNode,self.nodeTypes)
        
    """
    ####################################################################################
    The following are the "CRUD" (Create, read, update,delete) methods for the general handling of nodes
    """
    @defer.inlineCallbacks
    def add_addOn(self,name="node",description="",type=None,connector=None,driver=None,*args,**kwargs):
        """
        Add a new node to the list of nodes of the current environment
        Params:
        name: the name of the node
        Desciption: short description of node
        type: the type of the node : very important , as it will be used to instanciate the correct class
        instance
        Connector:the connector to use for this node
        Driver: the driver to use for this node's connector
        """
            
        if type in self.nodeTypes.iterkeys():
            node= yield Node(name,description,type).save()
            node.environment.set(self.parentEnv)
            self.nodes[node.id]=node
            capability= yield NodeManager.nodeTypes[type](name,description).save()
            capability.node.set(node)
            node.capability=capability
            
            log.msg("Added  node ",name," of capability ",type," with id set to ",str(node.id), logLevel=logging.CRITICAL)
            defer.returnValue(node)
        else:
            log.msg("unknown node type",logLevel=logging.CRITICAL)
            raise(UnknownNodeType())
        defer.returnValue(None)
    
    def get_addOns(self,filter=None):
        """
        Returns the list of nodes, filtered by  the filter param
        the filter is a dictionary of list, with each key beeing an attribute
        to check, and the values in the list , values of that param to check against
        """
        d=defer.Deferred()
        
        def filter_check(node,filter):
            for key in filter.keys():
                if not getattr(node, key) in filter[key]:
                    return False
            return True
      
        def get(filter,nodesList):
            if filter:
                return WrapperList(data=[node for node in nodesList if filter_check(node,filter)],rootType="nodes")
            else:               
                return WrapperList(data=nodesList,rootType="nodes")
            
        d.addCallback(get,self.nodes.values())
        reactor.callLater(0.5,d.callback,filter)
        return d
    
    def get_addOn(self,id):
        if not id in self.nodes.keys():
            raise NodeNotFound()
        return self.nodes[id]
    
    def update_addOn(self,id,name,description):
        """Method for addOn update"""
        return self.nodes[id]
        #self.nodes[id].update()
    
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
        reactor.callLater(0,d.callback,AddOnManager.addons)
        return d  
    
    @classmethod
    def update_addOns(cls):
        """
        wrapper method, for extraction+ list update in case of newly installed addons
        """
        AddOnManager.extract_addons()
        AddOnManager.list_addons()
        
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
   
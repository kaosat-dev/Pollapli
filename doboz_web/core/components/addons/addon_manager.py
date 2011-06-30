"""
.. py:module:: addon_manager
   :synopsis: manager of addons : add ons are packages of plugins + extras, and this manager handles the references
   to all of them
"""
import logging
import uuid
import pkgutil
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
    
    def get_nodes(self,filter=None):
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
    
    def get_node(self,id):
        if not id in self.nodes.keys():
            raise NodeNotFound()
        return self.nodes[id]
    
    def update_node(self,id,name,description):
        """Method for node update"""
        print("updating node")
        return self.nodes[id]
        #self.nodes[id].update()
    
    def delete_node(self,id):
        """
        Remove a node : this needs a whole set of checks, 
        as it would delete an node completely 
        Params:
        id: the id of the node
        """
        d=defer.Deferred()
        def remove(id,nodes):
            nodeName=nodes[id].name
            nodes[id].delete()
            del nodes[id]
            log.msg("Removed node ",nodeName,"with id ",id,logLevel=logging.CRITICAL)
        d.addCallback(remove,self.nodes)
        reactor.callLater(0,d.callback,id)
        return d
            
    @defer.inlineCallbacks
    def clear_addons(self):
        """
        Removes & deletes ALL the nodes, should be used with care
        """
        for node in self.nodes.values():
            yield self.delete_node(node.id)        
        defer.returnValue(None)
   
    @classmethod
    @defer.inlineCallbacks
    def get_plugins(cls,interface=None,addon=None):
        """
        method to get specific plugins
        """        
        plugins=[]
        addonpackages=pkgutil.walk_packages(path=[AddOnManager.addOnPath], prefix='')
        for loader,name,isPkg in addonpackages:            
            mod = pkgutil.get_loader(name).load_module(name)
            try:
                plugins.extend((yield getPlugins(interface,mod)))
            except Exception as inst:
                print("error in fetching plugin: %s"%str(inst))
        defer.returnValue(plugins)
    """
    ####################################################################################
    Helper Methods    
    """
    def enable_addon(self):
        pass
    
    def disable_addon(self):
        pass
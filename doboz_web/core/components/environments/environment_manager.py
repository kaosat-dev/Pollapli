"""
.. py:module:: environment_manager
   :synopsis: manager of environments.
"""
import os
import random
import logging
import time
import datetime
import shutil
import imp
import inspect
from twisted.internet import reactor, defer
from twisted.enterprise import adbapi
from twistar.registry import Registry
from twistar.dbobject import DBObject
from twistar.dbconfig.base import InteractionBase
from twisted.python import log,failure
from twisted.python.log import PythonLoggingObserver


from doboz_web.core.components.environments.environment import Environment
from doboz_web.exceptions import EnvironmentAlreadyExists
from doboz_web.core.components.nodes.node import Node
from doboz_web.core.components.automation.task import Task
from doboz_web.core.tools.wrapper_list import WrapperList
from doboz_web.core.components.connectors.hardware.hardware_connector import HardwareConnector
from doboz_web.core.components.connectors.hardware.serial.serial_connector import SerialConnector
#from doboz_web.core.components.nodes.hardware.reprap.reprap_node import ReprapNode
#from doboz_web.core.components.nodes.reprap_capability import ReprapCapability

Registry.register(Environment, Node)
Registry.register(Node, Task)
#Registry.register(Environment, Task)
Registry.register(Node, HardwareConnector)
Registry.register(Node, SerialConnector)
class EnvironmentManager(object):
    """
    Class acting as a central access point for all the functionality of environments
    """
    def __init__(self,envPath):
        self.logger=log.PythonLoggingObserver("dobozweb.core.components.environments.environmentManager")
        self.environments={}
        self.path=envPath
        self.idCounter=1
    
    @defer.inlineCallbacks
    def setup(self):
        #self.scan_plugins()
        self.startTime = time.time()
        """Retrieve all existing environments from disk"""
        maxFoundId=1
        for fileDir in os.listdir(self.path): 
            if os.path.isdir(os.path.join(self.path,fileDir)):        
                   
                envName= fileDir
                envPath=os.path.join(self.path,envName)
                dbPath=os.path.join(envPath,envName)+".db"
                if os.path.exists(dbPath):
                    Registry.DBPOOL = adbapi.ConnectionPool("sqlite3",database=dbPath,check_same_thread=False)
                                    
                    def addEnv(env,maxFoundId):
                        self.environments[env[0].id]=env[0]
                        env[0].setup()
                        if env[0].id>maxFoundId:
                            maxFoundId=env[0].id
                        
                        return maxFoundId
                    
                    maxFoundId=yield Environment.find().addCallback(addEnv,maxFoundId)
                    self.idCounter=maxFoundId+1
                    #temporary: this should be recalled from db from within the environments ?
        
        log.msg("Environment manager setup correctly", logLevel=logging.CRITICAL)
        
    def __getattr__(self, attr_name):
        for env in self.environments.values():
            if hasattr(env, attr_name):
                return getattr(env, attr_name)
        raise AttributeError(attr_name)
        
        
    def stop(self):
        """
        Shuts down the environment manager and everything associated with it : ie EVERYTHING !!
        Should not be called in most cases
        """
        pass

    """
    ####################################################################################
    The following are the "CRUD" (Create, read, update,delete) methods for the general handling of environements
    """
    @defer.inlineCallbacks
    def add_environment(self,name="home_test",description="Add Description here",status="frozen"):
        """
        Add an environment to the list of managed environements : 
        Automatically creates a new folder and launches the new environement auto creation
        Params:
        EnvName: the name of the environment
        description:a short description of the environment
        status: either frozen or live : whether the environment is active or not
        """
        envPath=os.path.join(self.path,name)  
        #if such an environment does not exist, add it
        
        if not name in os.listdir(self.path):
            os.mkdir(envPath)
            dbpath=os.path.join(envPath,name)+".db"
            Registry.DBPOOL = adbapi.ConnectionPool("sqlite3",database=dbpath,check_same_thread=False)
            
            
            env=Environment(path="toto",name=name,description=description,status=status)
            yield self._generateDatabase()
            yield env.save()  
            
            """rather horrid hack of sorts, required to have different, sequential id in the different dbs"""
            self.force_id(self.idCounter)  
            Registry.DBPOOL.close()
            Registry.DBPOOL = adbapi.ConnectionPool("sqlite3",database=dbpath,check_same_thread=False)
            
            def addEnv(env):
                self.environments[env[0].id]=env[0]
                self.idCounter+=1
            yield Environment.find().addCallback(addEnv)
            
            env=self.environments[self.idCounter-1]
            log.msg("Adding environment named:",name ," description:",description,"with id",env.id, logLevel=logging.CRITICAL)
            defer.returnValue(env)
        else:
            raise EnvironmentAlreadyExists()

        defer.returnValue(None) 
    

    def get_environments(self,filter=None):
        """
        Returns the list of environments, filtered by  the filter param
        the filter is a dictionary of list, with each key beeing an attribute
        to check, and the values in the list , values of that param to check against
        """
        d=defer.Deferred()
        
        def filter_check(env,filter):
            for key in filter.keys():
                if not getattr(env, key) in filter[key]:
                    return False
            return True
      
        def get(filter,envsList):
            if filter:
                #return [env for env in self.environments if getattr(env, "id") in filter["id"]]
                #return [env for env in self.environments if [True for key in filter.keys() if getattr(env, key)in filter[key]]]
              
                return WrapperList(data=[env for env in envsList if filter_check(env,filter)],rootType="environments")
            else:
                return WrapperList(data=envsList,rootType="environments")
            
        d.addCallback(get,self.environments.values())
        reactor.callLater(0.5,d.callback,filter)
        return d
    
    def get_environment(self,envId):
        return self.environments[envId]
    
    def update_environment(self,id,name,description,status):
        #print("updating env",id,name,description,status)
        return self.environments[id].update(name,description,status)
    
    def remove_environment(self,id):
        """
        Remove an environment : this needs a whole set of checks, 
        as it would delete an environment completely (very dangerous)
        Params:
        name: the name of the environment
        """
        d=defer.Deferred()
        def remove(id,envs,path):
            try:
                Registry.DBPOOL.close()
                envName=envs[id].name
                envPath=os.path.join(path,envName)    
                #self.environments[envName].shutdown()
                del envs[id]
                if os.path.isdir(envPath): 
                    shutil.rmtree(envPath)
                    log.msg("Removed environment ",envName,"with id ",id,logLevel=logging.CRITICAL)
            except:
                pass
                #should raise  specific exception
                #raise Exception("failed to delete env")
        d.addCallback(remove,self.environments,self.path)
        reactor.callLater(0,d.callback,id)
        return d
        #self.logger.critical("Removed and deleted envrionment: '%s' at : '%s'",envName,envPath) 
        
    @defer.inlineCallbacks
    def clear_environments(self):
        """
        Removes & deletes ALL the environments, should be used with care
        """
        print(self.environments)
        for env in self.environments.values():
            yield self.remove_environment(env.id)        
        defer.returnValue(None)
    """
    ####################################################################################
    Helper Methods    
    """
    @defer.inlineCallbacks
    def force_id(self,id):     
        query=   '''UPDATE environments SET id ='''+str(id)+''' where id=1'''
        yield Registry.DBPOOL.runQuery(query)
#        yield Registry.DBPOOL.runQuery('''UPDATE environments
#             SET id =%id where id=1
#             ''')
        defer.returnValue(None)
    
    @defer.inlineCallbacks
    def _generateMasterDatabase(self):
        yield Registry.DBPOOL.runQuery('''CREATE TABLE environments(
             id INTEGER PRIMARY KEY ,
             name TEXT,
             status TEXT NOT NULL DEFAULT "Live",
             description TEXT
             )''')
    @defer.inlineCallbacks
    def _generateDatabase(self):
        yield Registry.DBPOOL.runQuery('''CREATE TABLE environments(
             id INTEGER PRIMARY KEY,
             name TEXT,
             status TEXT NOT NULL DEFAULT "Live",
             description TEXT
             )''')
        
        yield Registry.DBPOOL.runQuery('''CREATE TABLE nodes(
             id INTEGER PRIMARY KEY AUTOINCREMENT,
             environment_id INTEGER NOT NULL,
             type TEXT NOT NULL ,
             name TEXT,          
             description TEXT,
            FOREIGN KEY(environment_id) REFERENCES environments(id) 
             )''')
        
        yield Registry.DBPOOL.runQuery('''CREATE TABLE reprap_capabilities(
             id INTEGER PRIMARY KEY AUTOINCREMENT,
             node_id INTEGER NOT NULL,
             info TEXT,
             FOREIGN KEY(node_id) REFERENCES nodes(id)  
             )''')
        
        yield Registry.DBPOOL.runQuery('''CREATE TABLE dummy_capabilities(
             id INTEGER PRIMARY KEY AUTOINCREMENT,
             node_id INTEGER NOT NULL,
             info TEXT,
             FOREIGN KEY(node_id) REFERENCES nodes(id)  
             )''')
      #FOREIGN KEY(node_id) REFERENCES nodes(id)  
        
        yield Registry.DBPOOL.runQuery('''CREATE TABLE tasks(
             id INTEGER PRIMARY KEY AUTOINCREMENT,
             node_id INTEGER NOT NULL,
             name TEXT,          
             description TEXT,
             type TEXT,
             params TEXT,
             FOREIGN KEY(node_id) REFERENCES nodes(id)  
             )''')
        yield Registry.DBPOOL.runQuery('''CREATE TABLE actions(
             id INTEGER PRIMARY KEY AUTOINCREMENT,
             task_id INTEGER NOT NULL,
             name TEXT,          
             description TEXT,
             FOREIGN KEY(task_id) REFERENCES tasks(id)
             )''')
        yield Registry.DBPOOL.runQuery('''CREATE TABLE conditions(
             id INTEGER PRIMARY KEY AUTOINCREMENT,
             task_id INTEGER NOT NULL,
             name TEXT,          
             description TEXT,
             FOREIGN KEY(task_id) REFERENCES tasks(id)
             )''')
        
        yield Registry.DBPOOL.runQuery('''CREATE TABLE hardware_connectors(
             id INTEGER PRIMARY KEY AUTOINCREMENT,
             node_id INTEGER NOT NULL,
             seperator TEXT NOT NULL ,
             speed INTEGER NOT NULL,
             FOREIGN KEY(node_id) REFERENCES nodes(id)        
             )''')
        yield Registry.DBPOOL.runQuery('''CREATE TABLE serial_connectors(
             id INTEGER PRIMARY KEY AUTOINCREMENT,
             node_id INTEGER NOT NULL,
             seperator TEXT NOT NULL ,
             speed INTEGER NOT NULL,          
             FOREIGN KEY(node_id) REFERENCES nodes(id)       
             )''')
        yield Registry.DBPOOL.runQuery('''CREATE TABLE drivers(
             id INTEGER PRIMARY KEY AUTOINCREMENT,
             node_id INTEGER NOT NULL,
             connector_id INTEGER NOT NULL,
             type TEXT NOT NULL ,
             name TEXT,          
             description TEXT
             
             )''')
        defer.returnValue(None)
#             
#             
#        Registry.DBPOOL.runQuery('''CREATE TABLE Sensors(
#             id INTEGER PRIMARY KEY AUTOINCREMENT,
#             env_id INTEGER NOT NULL,
#             node_id INTEGER NOT NULL,
#             auto_id INTEGER NOT NULL DEFAULT 1,
#             captureType TEXT NOT NULL,
#             captureMode TEXT NOT NULL DEFAULT "Analog",
#             dataStorage TEXT NOT NULL DEFAULT "Db",
#             type TEXT NOT NULL ,
#             realName TEXT NOT NULL,
#             name TEXT,
#             description TEXT,
#             FOREIGN KEY(env_id) REFERENCES Environments(id),
#             FOREIGN KEY(node_id) REFERENCES Nodes(id),
#             FOREIGN KEY(auto_id) REFERENCES Automation(id)
#             )''').addCallback(self._dbGeneratedOk)
#             
#        Registry.DBPOOL.runQuery('''CREATE TABLE Actors(
#            id INTEGER PRIMARY KEY AUTOINCREMENT,
#             env_id INTEGER NOT NULL,
#             node_id INTEGER NOT NULL,
#             auto_id INTEGER NOT NULL DEFAULT 1,
#             realName TEXT NOT NULL,
#             params TEXT,
#             name TEXT,
#             description TEXT,
#             FOREIGN KEY(env_id) REFERENCES Environments(id),
#             FOREIGN KEY(node_id) REFERENCES Nodes(id),
#             FOREIGN KEY(auto_id) REFERENCES Automation(id)
#             )''').addCallback(self._dbGeneratedOk) 
    
    
 
                
    
 


    
    
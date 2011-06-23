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
from doboz_web.core.components.environments.exceptions import EnvironmentAlreadyExists




class WrapperList(list):
    def __init__(self, data=[],rootType="environments"):
        list.__init__(self,data)
        self.rootType=rootType
        
    def _toDict(self):
        envDict={}
        envDict[self.rootType]={}
        envDict[self.rootType]["items"]=[item._toDict() for item in self]

        return envDict

class EnvironmentManager(object):
    """
    Class acting as a central access point for all the functionality of environments
    """
    def __init__(self,envPath):
        self.logger=log.PythonLoggingObserver("dobozweb.core.components.environmentManager")
        #self.environments={}
        self.environments=[]
        self.path=envPath
        self.setup()
    
    def setup(self):
        pass
    def setup_old(self):
        #self.scan_plugins()
        self.startTime = time.time()
        """Retrieve all existing environments from disk"""
        for fileDir in os.listdir(self.path):    
            if os.path.isdir(os.path.join(self.path,fileDir)):           
                envName= fileDir
                envPath=os.path.join(self.path,envName)
                env=Environment(envPath,envName,"")    
                env.setup()
                #self.environments[envName]=env
                self.environments.append(env)
                id=self.environments.index(env)
                self.environments[id].id=id
                #temporary: this should be recalled from db from within the environments ?
        #self.logger.critical("Environment manager setup correctly")
        log.msg("Environment manager setup correctly", logLevel=logging.CRITICAL)
        
    def __getattr__(self, attr_name):
        for env in self.environments:
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
        if not name in self.environments:
            if os.path.exists(envPath):
                 raise EnvironmentAlreadyExists()
            os.mkdir(envPath)
            #env=Environment(envPath,name,description)
            dbpath=os.path.join(envPath,name)+".db"
            Registry.DBPOOL = adbapi.ConnectionPool("sqlite3",database=dbpath,check_same_thread=False)
            
            env=Environment(path="toto",name=name,description=description,status=status)
            self.environments.append(env)
            yield self._generateDatabase()
            yield env.save()
            #env.setup()
            #self.environments[id].id=int(env.id)
            log.msg("Adding environment named:",name ," description:",description, logLevel=logging.CRITICAL)
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
                return []
            else:
                return WrapperList(data=envsList,rootType="environments")
            
        d.addCallback(get,self.environments)
        reactor.callLater(0.5,d.callback,filter)
        return d
    
    def get_environment(self,envId):
        return self.environments[envId]
    
    def update_environment(self,id,name,description,status):
        pass
    
    def remove_environment(self,id):
        """
        Remove an environment : this needs a whole set of checks, 
        as it would delete an environment completely (very dangerous)
        Params:
        name: the name of the environment
        """
        d=defer.Deferred()
        def remove(id,envs,path):
            Registry.DBPOOL.close()
            envName=envs[id].name
            envPath=os.path.join(path,envName)    
            #self.environments[envName].shutdown()
            del envs[id]
            if os.path.isdir(envPath): 
                shutil.rmtree(envPath)
            #raise Exception("mlkjlk")
        d.addCallback(remove,self.environments,self.path)
        reactor.callLater(0,d.callback,id)
        return d
        #self.logger.critical("Removed and deleted envrionment: '%s' at : '%s'",envName,envPath) 
        
    @defer.inlineCallbacks
    def clear_environments(self):
        print(self.environments)
        for env in self.environments:
            yield self.remove_environment(env.id-1)        
        defer.returnValue(None)
    """
    ####################################################################################
    Helper Methods    
    """
    @defer.inlineCallbacks
    def _generateMasterDatabase(self):
        yield Registry.DBPOOL.runQuery('''CREATE TABLE environments(
             id INTEGER PRIMARY KEY AUTOINCREMENT,
             name TEXT,
             status TEXT NOT NULL DEFAULT "Live",
             description TEXT
             )''')
    @defer.inlineCallbacks
    def _generateDatabase(self):
        yield Registry.DBPOOL.runQuery('''CREATE TABLE environments(
             id INTEGER PRIMARY KEY AUTOINCREMENT,
             name TEXT,
             status TEXT NOT NULL DEFAULT "Live",
             description TEXT
             )''')
            
        yield Registry.DBPOOL.runQuery('''CREATE TABLE nodes(
             id INTEGER PRIMARY KEY AUTOINCREMENT,
             env_id INTEGER NOT NULL,
             type_id INTEGER NOT NULL ,
             name TEXT,          
             description TEXT,
             FOREIGN KEY(env_id) REFERENCES Environments(id)
             )''')
        
        yield Registry.DBPOOL.runQuery('''CREATE TABLE tasks(
             id INTEGER PRIMARY KEY AUTOINCREMENT,
             env_id INTEGER NOT NULL,
             name TEXT,          
             description TEXT,
             FOREIGN KEY(env_id) REFERENCES Environments(id)
             )''')
        yield Registry.DBPOOL.runQuery('''CREATE TABLE actions(
             id INTEGER PRIMARY KEY AUTOINCREMENT,
             env_id INTEGER NOT NULL,
             task_id INTEGER NOT NULL,
             name TEXT,          
             description TEXT,
             FOREIGN KEY(env_id) REFERENCES Environments(id),
             FOREIGN KEY(task_id) REFERENCES Environments(id)
             )''')
        yield Registry.DBPOOL.runQuery('''CREATE TABLE conditions(
             id INTEGER PRIMARY KEY AUTOINCREMENT,
             env_id INTEGER NOT NULL,
             task_id INTEGER NOT NULL,
             name TEXT,          
             description TEXT,
             FOREIGN KEY(env_id) REFERENCES Environments(id),
             FOREIGN KEY(task_id) REFERENCES Environments(id)
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
    
    
    """
    ####################################################################################
    The following functions are typically hardware manager/hardware nodes and sensors related, pass through methods for the most part
    """
    def add_node(self,id,type,name,description="Add description here",params=None):
        """
        Add a hardware node to the specified environment
        Params:
        envName: the name of the environement
        title:the name of the node
        Desciption: short description of node
        NodeType: nodetype id
        """
        self.environments[id].add_node(type,params)
        
    def remove_node(self,id,nodeId):
        """
        Remove a hardware node from the specified environment
        Params:nodeId : the id of the node we want removed
        """
        self.environments[id].remove_node(nodeId)
        
    def add_actor(self,envId,type,port):
        pass
    def remove_actor(self,envId):
        pass
    
    def add_sensor(self,id,node,params):
        """
        Add a sensor to an environment 
        Params:
        EnvName: the name of the environment
        Title: title of the sensor
        """
        self.environments[id].add_sensor(node,params)
       
    def remove_sensor(self,id,sensorId):
        """
        Remove a sensor from an environment 
        Params:
        EnvName: the name of the environment
        sensorId: id of the sensor to remove
        """
        self.environments[id]   
    
    def add_sensorType(self,envName,title, description):
        """
        Add a sensor type to an environment 
        Params:
        EnvName: the name of the environment
        Title: title of the sensorType
        Description: short description of the sensor type
        """
        self.environments[envName].add_sensorType(title, description)
        
    def remove_sensorType(self,envName,sensorTypeId):
        """
        Remove a sensor type from an environment 
        Params:
        EnvName: the name of the environment
        sensorTypeId: id of the sensor type to remove
        """
        self.environments[envName].remove_sensorType(sensorTypeId)
        
    def get_sensorData(self,criteria,startDate,endDate):
        """
        returns the data from a specific sensor in a specific node, in a specific environment
        collected between the two specified dates
        envName, nodeId , sensorId can be lists
        pass it a list of dictionaries
        as such {'envName':envName,'nodeId':nodeId,'sensorId':sensorId,'startDate':startDate,'endDate':endDate}
        {envName:{nodeId:(sensorId,sensorId2,...),nodeId2:(sensorId,sensorId2},envName2:}
        """
        for elem in criteria:
           self.environments[elem['envName']].get_sensorData(elem['nodeId'],elem['sensorId'],starDate,endDate)
    """
    ####################################################################################
    The following methods are typically  scheduler related
    """       
    
    """Keeping things seperate or not ???? """
    def add_sensorSchedule(self,envName,target,targetParams,startTime,function,functionparams="",interval="",name="",description=""):
        self.environments[envName].add_sensorSchedule(target,targetParams,startTime,function,functionparams,interval,name,description)
        
    def add_sensorTrigger(self,envName,target,targetParams,params):
        pass
    
    def schedule_Node(self):
        self.environments[envName].add_task(target,targetParams,startTime,function,functionparams,interval,title,description)
    
    def add_task(self,envName,target,targetParams,startTime,function,functionparams="",interval="",name="",description=""):
        """
        Add task
        """
        self.environments[envName].add_task(target,targetParams,startTime,function,functionparams,interval,name,description)
    
    def remove_task(self,envId):
        pass
 

if __name__=="__main__":
    test=EnvironmentManager()
    test.setup()
    creationTest()

    
    
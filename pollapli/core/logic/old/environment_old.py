"""
.. py:module:: environment_manager
   :synopsis: all things environment related : environment class and environment manager class.
"""
import os, random, logging,imp,inspect, time, datetime, shutil, imp
from twisted.internet import reactor, defer
from twisted.enterprise import adbapi
from twistar.registry import Registry
from twistar.dbobject import DBObject
from twistar.dbconfig.base import InteractionBase
from twisted.python import log,failure
from twisted.python.log import PythonLoggingObserver


from pollapli.exceptions import EnvironmentAlreadyExists,EnvironmentNotFound
from pollapli.core.logic.components.nodes.node import Node
from pollapli.core.logic.components.automation.task import Task
from pollapli.core.logic.components.automation.print_action import PrintAction
from pollapli.core.logic.components.automation.action import Action
from pollapli.core.logic.tools.wrapper_list import WrapperList
from pollapli.core.logic.tools.signal_system import SignalHander
from pollapli.core.logic.components.drivers.driver import Driver
from pollapli.core.logic.components.nodes.node import NodeManager
from pollapli.core.logic.components.automation.task import TaskManager


class Environment2(DBObject):
    
    def __init__(self,path="/",name="home",description="Add Description here",status="active",*args,**kwargs):
        self.path=path
        self.name=name
        self.description=description
        self.status=status
        self._parent = None
       
    def __eq__(self, other):
        return self.name == other.name and self.description == other.description and self.status == other.status
    def __ne__(self, other):
        return not self.__eq__(other)
    
    def __str__(self):
        return "%s %s %s" %(self.name,self.description,self.status)

class Environment(DBObject):
    HASMANY = ['nodes']
    HASMANY = ['tasks']
    EXPOSE=["name","description","id","status","_tasks","_nodes"]
    
    def __init__(self,path="/",name="home",description="Add Description here",status="active",*args,**kwargs):
        DBObject.__init__(self,**kwargs)
        self.path=path
        self.name=name
        self.description=description
        self.status=status
        self._devices=NodeManager(self)
        self._tasks=TaskManager(self)
                 
    """
    ####################################################################################
    Configuration and shutdown methods
    """
    
    @defer.inlineCallbacks
    def setup(self):
        """
        Method configuring additional elements of the current environment
        """
        yield self._nodes.setup()
        yield self._tasks.setup()
        
        #create db if not existent else just connect to it
#        dbPath=self.path+os.sep+self.name+"_db"
#        if not os.path.exists(dbPath):    
#            self.db=db_manager_SQLLITE(dbPath)
#            self.db.add_environment(self.name,self.description)
#        else:
#            self.db=db_manager_SQLLITE(dbPath)
        log.msg("Environment ",self.name ,"with id", self.id," setup correctly", logLevel=logging.CRITICAL, system="environment")
        defer.returnValue(None)
        
    def tearDown(self):
        """
        Tidilly shutdown and cleanup after environment
        """
        #self._nodes.tearDown()     

    def get_environmentInfo(self):
        return self.name
        
    def _toDict(self):
        result={"environment":{"id":self.id,"name":self.name,"description":self.description,"status":self.status,"link":{"rel":"environment"}}}
        return result

    def __getattr__(self, attr_name):
        if hasattr(self._nodes, attr_name):
            return getattr(self._nodes, attr_name)
        elif hasattr(self._tasks, attr_name):
            return getattr(self._tasks, attr_name)
        else:
            raise AttributeError(attr_name)

    def update(self,name,description,status):
        self.status=status
        self.description=description
        log.msg("Environment ",name," updated succesfully",system="Environement manager",logLevel=logging.INFO)
        return self
        

Registry.register(Environment, Node)
Registry.register(Environment, Task)
Registry.register(Task, PrintAction)
Registry.register(Task, Action)
#Registry.register(Task, Condition)
Registry.register(Node, Driver)


class EnvironmentManager(object):
    """
    Class acting as a central access point for all the functionality of environments
    """
    envPath=None
    environments={}
    idCounter=1
    def __init__(self,envPath):
        self.logger=log.PythonLoggingObserver("dobozweb.core.components.environments.environmentManager")
        self.path=EnvironmentManager.envPath
        self.idCounter=EnvironmentManager.idCounter
        
        self._signal_channel="environment_manager"
        self.signalHandler=SignalHander(self._signal_channel)
    
    @classmethod
    @defer.inlineCallbacks
    def setup(cls,*args,**kwargs):
        """Retrieve all existing environments from disk"""
        maxFoundId=1
        for fileDir in os.listdir(EnvironmentManager.envPath): 
            if os.path.isdir(os.path.join(EnvironmentManager.envPath,fileDir)):        
                envName= fileDir
                envPath=os.path.join(EnvironmentManager.envPath,envName)
                dbPath=os.path.join(envPath,envName)+".db"
                if os.path.exists(dbPath):
                    Registry.DBPOOL = adbapi.ConnectionPool("sqlite3",database=dbPath,check_same_thread=False)
                    @defer.inlineCallbacks        
                    def addEnv(env,maxFoundId):
                        EnvironmentManager.environments[env[0].id]=env[0]
                        yield env[0].setup()
                        if env[0].id>maxFoundId:
                            maxFoundId=env[0].id
                        
                        defer.returnValue(maxFoundId)
                    
                    maxFoundId=yield Environment.find().addCallback(addEnv,maxFoundId)
                    EnvironmentManager.idCounter=maxFoundId+1
                    #temporary: this should be recalled from db from within the environments ?
        
        log.msg("Environment manager setup correctly", system="environement manager", logLevel=logging.CRITICAL)
        
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
        dbpath=os.path.join(envPath,name)+".db"
        
        #if such an environment does not exist, add it
        doCreate=True
        if name in os.listdir(self.path):
            if os.path.exists(os.path.join(self.path,name,dbpath)):
                doCreate=False
        else:
            os.mkdir(envPath)
        
        if doCreate:
            Registry.DBPOOL = adbapi.ConnectionPool("sqlite3",database=dbpath,check_same_thread=False)
            
            env=Environment(path=envPath,name=name,description=description,status=status)
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
            self.signalHandler.send_message("environment.created",self,env)
            log.msg("Adding environment named:",name ," description:",description,"with id",env.id, system="environment manager", logLevel=logging.CRITICAL)         
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
        env=self.environments.get(envId)
        if env is None:
            raise EnvironmentNotFound()
        return env
    
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
                            #self.logger.critical("Removed and deleted envrionment: '%s' at : '%s'",envName,envPath) 
                    log.msg("Removed environment ",envName,"with id ",id, system="environment manager",logLevel=logging.CRITICAL)
            except:
                pass
                #should raise  specific exception
                #raise Exception("failed to delete env")
        d.addCallback(remove,self.environments,self.path)
        reactor.callLater(0,d.callback,id)
        return d

        
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
        yield Registry.DBPOOL.runQuery('''CREATE TABLE addons(
             id INTEGER PRIMARY KEY,
             name TEXT,
             description TEXT,
             active boolean NOT NULL default true           
             )''')
        yield Registry.DBPOOL.runQuery('''CREATE TABLE environments(
             id INTEGER PRIMARY KEY,
             name TEXT,
             description TEXT,
             status TEXT NOT NULL DEFAULT "Live"
             )''')
        
        yield Registry.DBPOOL.runQuery('''CREATE TABLE nodes(
             id INTEGER PRIMARY KEY AUTOINCREMENT,
             environment_id INTEGER NOT NULL,
             type TEXT NOT NULL ,
             name TEXT,          
             description TEXT,
             recipe TEXT,
            FOREIGN KEY(environment_id) REFERENCES environments(id) 
             )''')
        
      #FOREIGN KEY(node_id) REFERENCES nodes(id)  
        yield Registry.DBPOOL.runQuery('''CREATE TABLE drivers(
             id INTEGER PRIMARY KEY AUTOINCREMENT,
             node_id INTEGER NOT NULL,
             driverType TEXT NOT NULL,
             deviceType TEXT NOT NULL ,
             deviceId TEXT,
             options BLOB  ,
             FOREIGN KEY(node_id) REFERENCES nodes(id)      
             )''')
        
        yield Registry.DBPOOL.runQuery('''CREATE TABLE tasks(
             id INTEGER PRIMARY KEY AUTOINCREMENT,
             environment_id INTEGER NOT NULL,
             name TEXT,          
             description TEXT,
             type TEXT,
             params TEXT,
             FOREIGN KEY(environment_id) REFERENCES environments(id)  
             )''')
        yield Registry.DBPOOL.runQuery('''CREATE TABLE actions(
             id INTEGER PRIMARY KEY AUTOINCREMENT,
             task_id INTEGER NOT NULL,
             actionType TEXT,          
             params TEXT,
             FOREIGN KEY(task_id) REFERENCES tasks(id)
             )''')
        yield Registry.DBPOOL.runQuery('''CREATE TABLE conditions(
             id INTEGER PRIMARY KEY AUTOINCREMENT,
             task_id INTEGER NOT NULL,
             name TEXT,          
             description TEXT,
             FOREIGN KEY(task_id) REFERENCES tasks(id)
             )''')
        
       
             
        yield Registry.DBPOOL.runQuery('''CREATE TABLE sensors(
             id INTEGER PRIMARY KEY AUTOINCREMENT,
             node_id INTEGER NOT NULL,
             captureType TEXT NOT NULL,
             captureMode TEXT NOT NULL DEFAULT "Analog",
             type TEXT NOT NULL ,
             realName TEXT NOT NULL,
             name TEXT,
             description TEXT,
             FOREIGN KEY(node_id) REFERENCES nodes(id)
             )''')
        
        yield Registry.DBPOOL.runQuery('''CREATE TABLE readings(
             id INTEGER PRIMARY KEY AUTOINCREMENT,
             node_id INTEGER NOT NULL,
             sensor_id INTEGER NOT NULL,
             data INTEGER NOT NULL,
             dateTime TEXT NOT NULL,
             FOREIGN KEY(node_id) REFERENCES nodes(id),
             FOREIGN KEY(sensor_id) REFERENCES sensors(id)
             )''')
        """this should be in the master db, but will have to do for now (only support for one environment,
        because of the limitations of twistar: one db )"""
        
        yield Registry.DBPOOL.runQuery('''CREATE TABLE updates(
             id INTEGER PRIMARY KEY AUTOINCREMENT,
             type TEXT NOT NULL,
             name TEXT NOT NULL,
             description TEXT,
             version TEXT NOT NULL,
             downloadUrl TEXT NOT NULL,
             tags TEXT NOT NULL,
             img TEXT NOT NULL,
             file TEXT NOT NULL,
             fileHash TEXT NOT NULL,
             downloaded TEXT NOT NULL,
             installed TEXT NOT NULL,
             enabled TEXT NOT NULL
             
             )''')
        
        defer.returnValue(None)
      
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
    
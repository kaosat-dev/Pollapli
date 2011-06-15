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

from doboz_web.core.components.environments.environment import Environment

class EnvironmentManager(object):
    """
    Class acting as a central access point for all the functionality of environments
    """
    def __init__(self,envPath):
        self.logger = logging.getLogger("dobozweb.core.components.environmentManager") 
        #self.environments={}
        self.environments=[]
        self.path=envPath
        self.setup()
    
    def setup(self):
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
        self.logger.critical("Environment manager setup correctly")
        
        
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
    The following functions are for the general handling of environements
    """
    def get_environments(self):
        """
        Returns the list of environments
        """
        return self.environments
    
    def get_environment(self,envId):
        return self.environments[envId]
    
    def add_environment(self,name,description="Add Description here",status="frozen"):
        """
        Add an environment to the list of managed environements : 
        Automatically creates a new folder and launches the new environement auto creation
        Params:
        EnvName: the name of the environment
        description:a short description of the environment
        status: either frozen or live : whether the environment is active or not
        """
        #create hash from envName
       
        envPath=os.path.join(self.path,name)  
       
       
        #if such an environment does not exist, add it
        if not name in self.environments:
            os.mkdir(envPath)
            env=Environment(envPath,name,description)
            env.setup()
            self.environments.append(env)
            id=self.environments.index(env)
            self.environments[id].id=id
            self.logger.critical("Adding environment named %s, description: %s",name,description)
            """ IF IT IS ALREADY PRESENT,  DISPATCH A " WARNING" MESSAGE"""
            return env
        
    def remove_environment(self,id):
        """
        Remove an environment : this needs a whole set of checks, 
        as it would delete an environment completely (very dangerous)
        Params:
        name: the name of the environment
        """
        envName=self.environments[id].name
        envPath=os.path.join(self.path,envName)#self.environments[name].path
        
       
        #self.environments[envName].shutdown()
        del self.environments[id]
        shutil.rmtree(envPath)
        
        self.logger.critical("Removed and deleted envrionment: '%s' at : '%s'",envName,envPath) 
        
    def clear_environments(self):
       
        for env in self.environments:
            envName=env.name
            envPath=os.path.join(self.path,envName)
            if os.path.isdir(envPath): 
                #del self.environments[self.environments.index(env)]
                shutil.rmtree(envPath)
        self.environments=[]
                
    def get_environementInfo(self,id):
        print(self.environments[id].get_environmentInfo())
    
    def get_data(self,params):
        pass
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

    
    
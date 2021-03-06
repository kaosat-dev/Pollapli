"""
.. py:module:: environment_manager
   :synopsis: all things environment manager related :environment manager class.
"""
import os, random, logging,imp,inspect, time, datetime, shutil, imp
from twisted.internet import reactor, defer
from twisted.python import log,failure
from pollapli.exceptions import EnvironmentAlreadyExists,EnvironmentNotFound
from pollapli.core.logic.tools.signal_system import SignalDispatcher
from pollapli.core.logic.components.environments.environment import Environment

class EnvironmentManager(object):
    """
    Class acting as a central access point for all the functionality of environments
    """
    def __init__(self,persistenceLayer = None):
        self._persistenceLayer = persistenceLayer
        self._logger=log.PythonLoggingObserver("dobozweb.core.components.environments.environmentManager")
        self._environments = {}
        self._signal_channel="environment_manager"
        self._signal_dispatcher = SignalDispatcher(self._signal_channel)
        
    def __getattr__(self, attr_name):
        for env in self._environments.values():
            if hasattr(env, attr_name):
                return getattr(env, attr_name)
        raise AttributeError(attr_name)  
      
    @defer.inlineCallbacks
    def setup(self,*args,**kwargs):
        """Retrieve all existing environments from disk"""
        environments = yield self._persistenceLayer.load_environments()
        for environment in environments:
            self._environments[environment.cid] = environment
            environment._persistenceLayer = self._persistenceLayer
            yield environment.setup()
        log.msg("Environment manager setup correctly", system="environement manager", logLevel=logging.INFO)
    
    def teardown(self):
        """
        Shuts down the environment manager and everything associated with it : ie EVERYTHING !!
        Should not be called in most cases
        """
        pass
        
    def _send_signal(self, signal="", data=None):
        prefix=self._signal_channel+"."
        self._signal_dispatcher.send_message(prefix+signal,self,data)    
    """
    ####################################################################################
    The following are the "CRUD" (Create, read, update,delete) methods for the general handling of environements
    """
    @defer.inlineCallbacks
    def add_environment(self,name="Default Environment",description="Add Description here",status="inactive"):
        """
        Add an environment to the list of managed environements : 
        Automatically creates a new folder and launches the new environement auto creation
        Params:
        name: the name of the environment
        description:a short description of the environment
        status: either frozen or live : whether the environment is active or not
        """
        for environment in self._environments.values():
            if environment.name == name:
                raise EnvironmentAlreadyExists()
        environment = Environment(persistenceLayer=self._persistenceLayer, name=name,description=description,status=status)
        yield self._persistenceLayer.save_environment(environment)
        self._environments[environment.cid] = environment
        
        self._send_signal("environment.created",environment)
        log.msg("Added environment named:",name ," description:",description,"with id",environment.cid, system="environment manager", logLevel=logging.CRITICAL)         
        defer.returnValue(environment)

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
      
        def _get_envs(filter,envsList):
            if filter:
                return [env for env in envsList if filter_check(env,filter)]
            else:
                return envsList
            
        d.addCallback(_get_envs,self._environments.values())
        reactor.callLater(0,d.callback,filter)
        return d
    
    
    def get_environment(self,id, *args, **kwargs):   
        if not id in self._environments.keys():
            raise EnvironmentNotFound() 
        else:
            #raise EnvironmentNotFound() 
            #defer.succeed(self._environments[id])
            return self._environments[id]
    
    def update_environment(self,id,name,description,status):
        environment = self._environments[id]
        environment.update(name,description,status)
        self._send_signal("environment_updated", environment)
        #return self.environments[id].update(name,description,status)
    
    @defer.inlineCallbacks
    def remove_environment(self,id=None,name=None):
        """
        Remove an environment : this needs a whole set of checks, 
        as it would delete an environment completely (very dangerous)
        Params:
        name: the name of the environment
        """
        try:
            environment = self._environments[id]
            yield self._persistenceLayer.delete_environment(environment)
            #self.environments[envName].teardown()
            del self._environments[id]
            self._send_signal("environment_deleted", environment)
            log.msg("Removed environment ",environment.name, system="environment manager",logLevel=logging.CRITICAL)
        except Exception as inst:
            raise Exception("Failed to delete environment because of error %s" %str(inst))
        
#        d = defer.Deferred()
#        def remove(id,envs):
#            try:
#                environment = envs[id]
#                yield self._persistenceLayer.delete_environment(environment)
#                envPath=os.path.join(FileManager.dataPath,environment._name)
#                #self.environments[envName].teardown()
#                del envs[id]
#                if os.path.isdir(envPath): 
#                    shutil.rmtree(envPath)
#                    log.msg("Removed environment ",environment._name, system="environment manager",logLevel=logging.CRITICAL)
#            except:
#                raise Exception("Failed to delete environment")
#                #should raise  specific exception
#                
#        d.addCallback(remove,self._environments)
#        reactor.callLater(0,d.callback,id)
#        return d

        
    @defer.inlineCallbacks
    def clear_environments(self):
        """
        Removes & deletes ALL the environments, should be used with care
        """
        for envId in self._environments.keys():
            yield self.remove_environment(id = envId)    
        self._send_signal("environments_cleared", self._environments)       
    """
    ####################################################################################
    Helper Methods    
    """
  
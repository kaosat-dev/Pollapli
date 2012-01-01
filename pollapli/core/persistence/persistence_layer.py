import os, shutil
from twisted.internet import reactor, defer
from pollapli.core.persistence.dao_base.dao_manager_factory import DaoManagerFactory
from pollapli.exceptions import EnvironmentNotFound


class PersistenceLayer(object):
    def __init__(self, pathManager=None):
        self._path_manager = pathManager
        self._daoManager = DaoManagerFactory(pathManager=self._path_manager).create_dao_manager("sqlite")

    def __getattr__(self, attr_name):
        if hasattr(self._daoManager, attr_name):
            return getattr(self._daoManager, attr_name)
        else:
            raise AttributeError(attr_name)

    def tearDown(self):
        self._daoManager.tearDown()

    @defer.inlineCallbacks
    def save_environment(self, environment=None, *args, **kwargs):
        if self._path_manager is None:
                raise EnvironmentNotFound("Path manager not set, cannot delete environment files")
        environmentPath = os.path.join(self._path_manager.dataPath, environment.name)
        if not os.path.exists(environmentPath):
            os.makedirs(environmentPath)
        yield self._daoManager.save_environment(environment,*args,**kwargs)

    @defer.inlineCallbacks
    def save_environments(self, lEnvironment):
        if self._path_manager is None:
                raise EnvironmentNotFound("Path manager not set, cannot delete environment files")
        for environment in lEnvironment:
            environmentPath = os.path.join(self._path_manager.dataPath, environment.name)
            if not os.path.exists(environmentPath):
                os.makedirs(environmentPath)
        yield self._daoManager.save_environments(lEnvironment)

    @defer.inlineCallbacks
    def delete_environment(self, environment=None):
        #TODO: improve path handing
        if self._path_manager is None:
            raise EnvironmentNotFound("Path manager not set, cannot delete environment files")
        
        yield self._daoManager.delete_environment(environment)
        environmentPath = os.path.join(self._path_manager.dataPath,environment.name)
        if os.path.exists(environmentPath) and os.path.isdir(environmentPath):
            shutil.rmtree(environmentPath)
            
    @defer.inlineCallbacks
    def delete_environments(self, lEnvironment ):
        if self._path_manager is None:
            raise EnvironmentNotFound("Path manager not set, cannot delete environment files")
        for environment in lEnvironment:    
            yield self._daoManager.delete_environment(environment)
            environmentPath = os.path.join(self._path_manager.dataPath,environment.name)
            if os.path.exists(environmentPath) and os.path.isdir(environmentPath):
                shutil.rmtree(environmentPath)
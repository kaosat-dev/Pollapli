import abc
from twisted.internet import reactor, defer,task
from twisted.python import log,failure
from twisted.python.log import PythonLoggingObserver
from twisted.plugin import getPlugins,IPlugin
from twisted.web import client
from twistar.registry import Registry
from twistar.dbobject import DBObject
from twistar.dbconfig.base import InteractionBase 
from doboz_web.core.persistance.dao_base.update_dao import UpdateDao
from doboz_web.core.logic.components.updates.update_manager import Update

class UpdateSqliteDao(UpdateDao):
    def __init__(self,*args,**kwargs):
        pass
         
    def load_update(self,*args,**kwargs):
        """Retrieve data from update object."""
        #Update.load()
    
    def load_updates(self,*args,**kwargs):
        """Retrieve multiple update objects."""
        return
    
    def load_all_updates(self,*args,**kwargs):
        """Retrieve all update objects."""
        return
    
    def save_update(self, update):
        """Save the update object ."""
        return
    
   
    
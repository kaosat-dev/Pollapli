import os
from twisted.trial import unittest
from twisted.enterprise import adbapi 
from twisted.internet import reactor, defer
from twisted.python import log,failure
from pollapli.core.persistence.sqlite.driver_sqlite_dao import DriverSqliteDao
#from pollapli.core.logic.components.drivers.driver import Driver


class DriverSqliteDaoTests(unittest.TestCase):    
    
    
    def setUp(self):
        pass
        #self._dbpool = adbapi.ConnectionPool("sqlite3",'pollapli.db',check_same_thread=False)
        #self._driverSqliteDao=DriverSqliteDao(self._dbpool)
        
#    @defer.inlineCallbacks
#    def tearDown(self):
#        yield self._dbpool.close()
#        os.remove('pollapli.db')
   
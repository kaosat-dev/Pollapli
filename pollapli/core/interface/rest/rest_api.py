import logging
from twisted.python import log
from twisted.web.resource import Resource
from pollapli.core.interface.rest.handlers.config_handlers import ConfigHandler
from pollapli.core.interface.rest.handlers.driver_handlers import DriverTypesHandler
from pollapli.core.interface.rest.handlers.environment_handlers import EnvironmentsHandler

class RestApi(object):
    def __init__(self,root = None):
        restRoot=Resource()
        root.putChild("rest",restRoot)
        try:
            restRoot.putChild("config", ConfigHandler("/rest/config"))
            restRoot.putChild("drivertypes", DriverTypesHandler("/rest/drivertypes")) 
            restRoot.putChild("environments", EnvironmentsHandler("/rest/environments",self.environmentManager))
        except Exception as inst:
            log.msg("Error in base rest resources creation",str(inst), system="server", logLevel=logging.CRITICAL)
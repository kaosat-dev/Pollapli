from twisted.application import internet, service
from pollapli.pollapli_services import PollapliCoreServer,PollapliRestServer

application = service.Application("pollapli")
coreServer=PollapliCoreServer()
restServer=PollapliRestServer()

coreServer.setServiceParent(application)
restServer.setServiceParent(application)

from twisted.application import internet, service
from doboz_web.pollapli_services import PollapliCoreServer,PollapliRestServer

application = service.Application("pollapli")
coreServer=PollapliCoreServer()
restServer=PollapliRestServer()

coreServer.setServiceParent(application)
restServer.setServiceParent(application)

from twisted.application import internet, service



class PollapliCoreServer(service.Service):
    def __init__(self):
        pass

class PollapliRestServer (service.Service):
    def __init__(self):
        root = File(self.filePath)
        restRoot=Resource()
        root.putChild("rest",restRoot)
        try:
            restRoot.putChild("config", ConfigHandler("/rest/config"))
            restRoot.putChild("drivertypes", DriverTypesHandler("/rest/drivertypes")) 
            restRoot.putChild("environments", EnvironmentsHandler("/rest/environments",self.environmentManager))
        except Exception as inst:
            log.msg("Error in base rest resources creation",str(inst), system="server", logLevel=logging.CRITICAL)
             
        factory = Site(root)
   
        reactor.listenTCP(self.port, factory)
        log.msg("Server started!", system="server", logLevel=logging.CRITICAL)
        reactor.run()
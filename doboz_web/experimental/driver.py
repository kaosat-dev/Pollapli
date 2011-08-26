class Driver(object):
    def build_test(self):
        self.hw=HardwareHandlerBuilder()
        hw1=self.hw.buildHandler("SerialHardwareHandler","BaseProtocol")
        if hw1 is not None:
            hw1=hw1.result
            print("HW HANDLR",hw1)
            try:
            
                hw2=hw1(self)
                print("qsd",hw2)
            except Exception as inst:
                print("error",inst)
class HardwareHandlerBuilder(object):
    def __init__(self):
        pass
    @defer.inlineCallbacks
    def buildHandler(self,handlerType,protocolType,**params):
        hwHandlerKlass=None
        protocolKlass=None
        
        hwHandler=None
        hwHandlers= (yield UpdateManager.get_plugins(idoboz_web.IDriverHardwareHandler))
        print("harwareHandlers",hwHandlers)
        for hKlass in hwHandlers:
            if handlerType.lower()==hKlass.__name__.lower():
                hwHandlerKlass=hKlass    
            break
        
        protocols= (yield UpdateManager.get_plugins(IProtocol))
        print("protocols",protocols)
        for pKlass in hwHandlers:
            if protocolType.lower()==pKlass.__name__.lower():
                protocolKlass=pKlass    
            break
        
        defer.returnValue(hwHandler)
from doboz_web.core.components.drivers.driver import Driver

class GenericDriver(Driver):
    """A generic all purpose Driver class, with no data formating save for newline"""
    def __init__(self,category="reprap",speed=115200,seperator="\n",bufferSize=1):
        Driver.__init__(self,category,speed,seperator,bufferSize)
        
    def _handle_machineInit(self,datablock):
        if datablock  :
            self.remoteInitOk=True
            self.logger.critical("Machine Initialized")
        else:
            raise Exception("Machine NOT Initialized")
            
    def _format_data(self,datablock,*args,**kwargs):
        return datablock+ "\n"
    
      
        
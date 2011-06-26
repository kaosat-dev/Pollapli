class BaseProtocolTest(Protocol):
    def __init__(self,factory):
        self.factory=factory
        
    def connectionMade(self):
        self.factory._validate_connection(self)
    def dataReceived(self, data):
        try:
            self.factory._handle_data(data)
        except Exception as inst:
            print("error in serial",str(inst))
            #self.state = getattr(self, 'state_'+self.state)(byte)
    def connectionLost(self, reason='connectionDone'):
        print (reason)
        
#        def get_data(self):
#        """
#        Main funtion for getting the data recievd on the serial port
#        If attemps to get the serial data fail,shutdown
#        """
#        data=None
#        if self.isConnected :
#            try:
#                waiting=self.serial.inWaiting()
#                if waiting>0:
#                    self.logger.debug("waiting for data")
#                    data=self.serial.read(waiting)
#            except Exception,e:
#                self.logger.critical("critical failure while getting serial data %s",str(e))
#                self.currentErrors+=1
#                #after ten failed attempts , shutdown
#                if self.currentErrors>self.maxErrors:
#                    self.events.disconnected(self,None)
#                    self.connect()
#                    
#        return data



class SerialTwisted_old(Factory):#factory
    protocol = BaseProtocolTest
    def __init__(self):
        self.port="Com4"
        self.speed=115200
        self.serial=SerialPort(BaseProtocolTest(self),self.port,reactor,baudrate=self.speed)
    def pouet(self,data):
        print("data",data)
    def _toDict(self):
        return {"connector":{"type":"SerialTwisted","params":{"speed":self.speed,"port":self.port},"link":{"rel":"connector"}}}

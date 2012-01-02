from doboz_web.core.components.drivers.driver import Driver

class FiveDDriver(Driver):
    """Makerbot Driver class: NOT FUNCTIONNAL FOR NOW !!"""
    def __init__(self,category="reprap",speed=38400,seperator="\n",bufferSize=8):
        Driver.__init__(self,category,speed,seperator,bufferSize)
        self.currentLine=1
        
    def _handle_machineInit(self,datablock):
        if "start" in datablock :
            self.remoteInitOk=True
            self.logger.critical("Machine Initialized")
        else:
            raise Exception("Machine NOT INITIALIZED")
        
    def _compare_firmware_version(self,version):
        pass    
    
    def _format_data(self,datablock,*args,**kwargs):
        """
        Cleanup gcode : remove comments and whitespaces
        """
        
        datablock=datablock.split(';')[0]
        datablock=datablock.strip()
        datablock=datablock.replace(' ','')
        datablock=datablock.replace("\t",'')
        
        prefix=0xD5
        packetLng=len(datablock)
        
        """Makerbot crc uses the dalas 1 wire crc :
        Polynomial = X8 + X5 + X4 + 1
        """
        crc=0
        """
        crc = (crc ^ data) & 0xff; // i loathe java's promotion rules
        for (int i = 0; i < 8; i++) {
            if ((crc & 0x01) != 0) {
                crc = ((crc >>> 1) ^ 0x8c) & 0xff;
            } else {
                crc = (crc >>> 1) & 0xff;
            }
        }
        """

        """Makerbot Syntax: Prefix <packageLength> <cmd> *<chksum>"""
       
       
      
            
        self.currentLine+=1
        
        return datablock+'*'+str(checksum)+"\n"
        
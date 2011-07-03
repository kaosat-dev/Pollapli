from zope.interface import implements
from twisted.plugin import IPlugin
from doboz_web import idoboz_web 
from zope.interface import classProvides
from doboz_web.core.components.connectors.driver import Driver

class FiveDDriver(Driver):
    classProvides(IPlugin, idoboz_web.IDriver)
    """Driver class: intermediary element that formats commands according to a spec before they get sent to the connector"""
    def __init__(self,type="reprap",speed=19200,seperator="\n",bufferSize=8):
        Driver.__init__(self,type,"serial",speed,seperator,bufferSize)
        self.currentLine=1
        
    def _handle_machineInit(self,datablock):
        if "start" in datablock :
            self.remoteInitOk=True
            self.logger.critical("Machine Initialized")
        else:
            raise Exception("Machine NOT INITIALIZED")
    def _format_data(self,datablock,*args,**kwargs):
        """
        Cleanup gcode : remove comments and whitespaces
        """
        
        datablock=datablock.split(';')[0]
        datablock=datablock.strip()
        datablock=datablock.replace(' ','')
        datablock=datablock.replace("\t",'')

        """RepRap Syntax: N<linenumber> <cmd> *<chksum>\n"""
        datablock = "N"+str(self.currentLine)+' '+datablock+''
        print("datablock",datablock)
        """ chksum = 0 xor each byte of the gcode (including the line number and trailing space)
        """     
        checksum = 0
        for c in datablock:
            checksum^=ord(c)
            
        self.currentLine+=1
        
        return datablock+'*'+str(checksum)+"\n"
        
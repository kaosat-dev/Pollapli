from zope.interface import implements
from twisted.plugin import IPlugin
from pollapli import ipollapli 
from zope.interface import classProvides
from pollapli.core.logic.components.connectors.driver import Driver

class ThingyDriver(Driver):
    classProvides(IPlugin, ipollapli.IDriver)
    """Driver class: intermediary element that formats commands according to a spec before they get sent to the connector"""
    def __init__(self,type="reprap",speed=115200,seperator="\n",bufferSize=8):
        Driver.__init__(self,type,speed,seperator,bufferSize)
    def _handle_machineInit(self,datablock):
        if "start" in datablock  :
            self.remoteInitOk=True
            self.logger.critical("Machine Initialized")
        else:
            raise Exception("Machine NOT INITIALIZED")
            
    def _format_data(self,datablock,*args,**kwargs):
        datablock=datablock.split(';')[0]
        datablock=datablock.strip()
        datablock=datablock.replace(' ','')
        datablock=datablock.replace("\t",'')
        print("here")

        return datablock+ "\n"
    
      
        
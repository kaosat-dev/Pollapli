"""
.. py:module:: idoboz_web
   :synopsis: all interface definitions
"""
from zope.interface import Interface, Attribute
from twisted.plugin import IPlugin

class IConnector(Interface):
    """
    Connector class , encapsulating a driver and its connection
    """

class ITestPlugin(Interface):
    """
    An object with specific physical properties
    """
    
    def doAThing(data):
        """
        Bla bla

        @type data: C{string}
        @param data: justdata
        """
        
class IDriver(Interface):
    """
    An object with specific physical properties
    """
    
class IDriverLogicHandler(Interface):
    """
    Class to handle the higher level logic of drivers : for example command queues etc
    """
    def _handle_request(self,data,*args,**kwargs):
        """
        Manages command requests
        @type data: C{string}
        @param data:  the raw request that needs to be pre-treated

        @rtype: C{object}
        @return: an encapsulated (or not) version of the raw request data
        """               
    def _handle_response(self,data):
        """
        Manages command responses and if a correct response is recieved , send a message into the 
        signal/message system
        
        @type data: C{string}
        @param data:  the raw response that needs to be pre-treated

        @rtype: C{object}
        @return: an encapsulated (or not) version of the raw request data
        """
        
class IDriverHardwareHandler(Interface):
    """
    Class to handle the lower level logic of drivers the actual hardware interactions:
     for example connecting/disconnecting devices, the protocol that is used etc
    """
    def connect(self):
        """
        establish connection to the device
        """
    def disconnect(self):
        """
        shut down connection to the device
        """
        
class IDriver_old(Interface):
    """
    An object with specific physical properties
    """
    def _format_data(datablock):
        """
        returns a formated version of the datablock
        this is for outgoing data only
        
        @type datablock: C{string}
        @param datablock:  the raw response that needs to be treated

        @rtype: C{string}
        @return: formated datablock
        """
    def _handle_machineInit(self,datablock):
        """
        handles machine (hardware node etc) initialization
        datablock: the incoming data from the machine
        @type datablock: C{string}
        @param datablock:  the raw response that needs to be treated

        @rtype: C{None}
        @return: Nothing
        """
    def handle_request(datablock,*args,**kwargs):
        """
        Manages command requests
        @type datablock: C{string}
        @param datablock:  the raw response that needs to be treated
        
        @rtype: C{None}
        @return: Nothing
        """
    def get_next_command():
        """Returns next avalailable command in command queue 
        
        @rtype: C{string}
        @return: returns the next command in queue formated by _format_data 
        """
    def handle_answer(datablock):
        """handles only commands that got an answer, formats them correctly and sets necesarry flags
        @type datablock: C{string}
        @param datablock:  the raw response that needs to be treated
        
        @rtype: C{None}
        @return: Nothing
        """
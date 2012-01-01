from pollapli.addons.ReprapAddOn_0_0_1_py2_6.reprap.base_reprap_driver import BaseReprapDriver
from twisted.plugin import IPlugin
from pollapli import ipollapli
from zope.interface import classProvides
from pollapli.core.hardware.drivers.protocols import BaseTextSerialProtocol


class TeacupReprapProtocol(BaseTextSerialProtocol):
    """
    Class defining the protocol used by this driver: in this case, the reprap teacup protocol 
    which is the most straighforward of reprap protocols (no checksum etc)
    """
    def __init__(self, driver=None, handshake="start", seperator='\n', *args, **kwargs):
        BaseTextSerialProtocol.__init__(self, driver, handshake, seperator)


class TeacupReprapDriver(BaseReprapDriver):
    """Class defining the components of the driver for the teacup reprap firmware """
    classProvides(IPlugin, ipollapli.IDriver)
    target_hardware = "Reprap"

    """ generic"""
    def get_firmware_version(self):
        self.send_command("M115")

    def set_debug_level(self,level):
        self.send_command("M111")

    def init(self):
        self.send_command("")

    def startup(self):
        self.send_command("M190")

    def shutdown(self):
        self.send_command("M191")

    def queue_position(self, position, extended=False, absolute=True, rapid=False):
        if rapid:
            self.send_command("G1%s" % str(position))

    def get_position(self, extended=False):
        self.send_command("M114")

    def set_position(self, position, extended=False):
        self.send_command("G92%s" % str(position))

    def save_homePosition(self):
        self.send_command("G92")

    def load_homePosition(self):
        """not implemented"""

    def go_homePosition(self):
        self.send_command("G28")

    def set_unit(self, unit="mm"):
        if unit == "mm":
            self.send_command("G21")
        elif unit == "inch":
            self.send_command("G20")
    """"""
    #tools
    def tool_query(self, toolIndex):
        pass

    def tool_command(self):
        pass

    def change_tool(self):
        self.send_command("M6")

    def wait_forTool(self):
        pass

"""Reference for checksum calculation"""
#        """RepRap Syntax: N<linenumber> <cmd> *<chksum>\n"""
#        data = "N"+str(self.currentLine)+' '+data+''
#        
#        """ chksum = 0 xor each byte of the gcode (including the line number and trailing space)
#        """     
#        checksum = 0
#        for c in data:
#            checksum^=ord(c)
#            
#        self.currentLine+=1
#        
#        return data+'*'+str(checksum)+"\n"

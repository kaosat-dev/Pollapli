from twisted.plugin import IPlugin
from pollapli import ipollapli
from zope.interface import classProvides
from pollapli.addons.ReprapAddOn.reprap.hardware.reprap_base_driver import ReprapBaseDriver
from pollapli.core.hardware.drivers.serial_hardware_interface import SerialHardwareInterface
from pollapli.core.hardware.drivers.protocols import BaseTextSerialProtocol

class Reprap5dProtocol(BaseTextSerialProtocol):
    target_firmware = "*"
    """
    Class defining the protocol used by this driver: in this case, the reprap 5d protocol 
    """
    def __init__(self, driver=None, handshake="start", seperator='\n', do_checksum=False, *args, **kwargs):
        BaseTextSerialProtocol.__init__(self, driver, handshake, seperator)
        self.do_checksum = do_checksum
        self.line_count = 0

    def _format_data_out(self,data,*args,**kwargs):
        """
        RepRap Syntax: N<linenumber> <cmd> *<chksum>\n
        chksum = 0 xor each byte of the gcode (including the line number and trailing space)
        """
        data=data.split(';')[0]
        data=data.replace("\t",'')

        if self.do_checksum:
            data = "N%i %s" % (self.line_count, data)
            self.line_count += 1
            checksum = 0
            for c in data:
                checksum ^= ord(c)
            data = "%s*%s" % (data, str(checksum))
        return data + "\n"


class ReprapTeacupDriver(ReprapBaseDriver):
    """Driver class for the teacup reprap firmware"""
    classProvides(IPlugin, ipollapli.IDriver)
    target_hardware = "Reprap"

    def __init__(self, auto_connect=False, max_connection_errors=3,
        connection_timeout=0, do_hanshake=True, do_authentifaction=True,
        speed=115200, *args, **kwargs):
        ReprapBaseDriver.__init__(self, auto_connect, max_connection_errors, connection_timeout, do_hanshake, do_authentifaction,*args, **kwargs)
        self._hardware_interface = SerialHardwareInterface(self, Reprap5dProtocol, True, speed, do_linecount=True, do_checksum=True,*args, **kwargs)

    def startup(self):
        return self.send_command("M190")

    def shutdown(self):
        return self.send_command("M191")

    def get_firmware_info(self):
        return self.send_command("M115")

    def set_debug_level(self,level):
        return self.send_command("M111")

    def enqueue_position(self, position, rapid=False):
        if rapid:
            return self.send_command("G1 %s" % str(position))
        else:
            return self.send_command("G0 %s" % str(position))
        
    def get_position(self, extended=False):
        return self.send_command("M114")

    def set_position(self, position, extended=False):
        return self.send_command("G92 %s" % str(position))

    def save_homePosition(self):
        return self.send_command("G92")

    def load_homePosition(self):
        """not implemented"""

    def go_homePosition(self):
        return self.send_command("G28")

    def set_unit(self, unit="mm"):
        if unit == "mm":
            return self.send_command("G21")
        elif unit == "inch":
            return self.send_command("G20")
    """"""
    #tools
    def tool_query(self, toolIndex):
        pass

    def tool_command(self):
        pass

    def change_tool(self):
        return self.send_command("M6")

    def wait_forTool(self):
        pass

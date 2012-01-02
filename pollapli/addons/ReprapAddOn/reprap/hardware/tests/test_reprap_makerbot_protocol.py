from twisted.trial import unittest
from twisted.internet import defer, reactor
from pollapli.addons.ReprapAddOn.reprap.hardware.reprap_makerbot_driver import ReprapMakerbotProtocol,\
    ReprapMakerbotDriver
import struct

class TestReprapMakerbotProtocol(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

#    def test_format_data_out_get_position(self):
#        reprap_makerbot_protocol = ReprapMakerbotProtocol(driver=ReprapMakerbotDriver(), do_checksum=True)
#        input = "21"
#        
#        obs_data = reprap_makerbot_protocol._format_data_out(input)
#        exp_data = ""
#        self.assertEquals(obs_data, exp_data)
        
        
    def test_format_data_in_get_position(self):
        reprap_makerbot_protocol = ReprapMakerbotProtocol(driver=ReprapMakerbotDriver(), do_checksum=True)
#        format = "<bbbIb"
#        sz = struct.calcsize(format)
#        input = struct.pack(format,"0xD5","0x10","0x21",32,"0x00")
#        print(input)
        
        format = "<BbbIb"
        sz = struct.calcsize(format)
        input = struct.pack(format,213,10,129,3568,13)
        output = struct.unpack(format, input)
        
        obs_data = reprap_makerbot_protocol._format_data_in(input)
#        exp_data = ""
#        self.assertEquals(obs_data, exp_data)

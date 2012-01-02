from twisted.trial import unittest
from twisted.internet import defer, reactor
from pollapli.addons.ReprapAddOn.reprap.hardware.reprap_teacup_driver import Reprap5dProtocol,\
    ReprapTeacupDriver

class TestReprap5dProtocol(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_format_data_out_checksum(self):
        reprap_5d_protocol = Reprap5dProtocol(driver=ReprapTeacupDriver(), do_checksum=True)
        input = "G1 X10 Y25.2"
        
        obs_data = reprap_5d_protocol._format_data_out(input)
        exp_data = "N0 G1 X10 Y25.2*51\n"
        self.assertEquals(obs_data, exp_data)
        
    def test_format_data_out_checksum_multiple_lines(self):
        reprap_5d_protocol = Reprap5dProtocol(driver=ReprapTeacupDriver(), do_checksum=True)
        input =["G1 X10 Y25.2", "G1 Z5.2", "G0 F5.2", "T0", "G92 E0", "G28",
                 "G1 F1500.0", "G1 X2.0 Y2.0 F3000.0", "G1 X3.0 Y3.0"]
        obs_data = []
        for line in input:
            obs_data.append(reprap_5d_protocol._format_data_out(line))
        exp_data = ["N0 G1 X10 Y25.2*51\n" ,"N1 G1 Z5.2*122\n" , "N2 G0 F5.2*100\n",
                    "N3 T0*57\n", "N4 G92 E0*67\n", "N5 G28*22\n", "N6 G1 F1500.0*82\n",
                    "N7 G1 X2.0 Y2.0 F3000.0*85\n", "N8 G1 X3.0 Y3.0*33\n"]
        self.assertEquals(obs_data, exp_data)

    def test_format_data_out_nochecksum(self):
        reprap_5d_protocol = Reprap5dProtocol(driver=ReprapTeacupDriver(), do_checksum=False)
        input = "G1 X10 Y25.2"
        
        obs_data = reprap_5d_protocol._format_data_out(input)
        exp_data = "G1 X10 Y25.2\n"
        self.assertEquals(obs_data, exp_data)
        
    def test_format_data_out_nochecksum_multiple_lines(self):
        reprap_5d_protocol = Reprap5dProtocol(driver=ReprapTeacupDriver(), do_checksum=False)
        input =["G1 X10 Y25.2", "G1 Z5.2", "G0 F5.2", "T0", "G92 E0", "G28",
                 "G1 F1500.0", "G1 X2.0 Y2.0 F3000.0", "G1 X3.0 Y3.0"]
        obs_data = []
        for line in input:
            obs_data.append(reprap_5d_protocol._format_data_out(line))
        exp_data = ["G1 X10 Y25.2\n" ,"G1 Z5.2\n" , "G0 F5.2\n",
                    "T0\n", "G92 E0\n", "G28\n", "G1 F1500.0\n",
                    "G1 X2.0 Y2.0 F3000.0\n", "G1 X3.0 Y3.0\n"]
        self.assertEquals(obs_data, exp_data)

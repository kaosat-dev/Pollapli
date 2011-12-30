from twisted.trial import unittest
from twisted.internet import defer, reactor
from pollapli.addons.ReprapAddOn_0_0_1_py2_6.reprap.Tools.gcode_parser import GCodeParser

class TestDriverManagerExampleArduinoDriver(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_position_gcode(self):
        iGCodeParser = GCodeParser()
        gcodeLine = "G0 X1"
        command  = iGCodeParser.parse(gcodeLine)
        self.assertEquals(command, "")
        
    def test_othercommand_gcode(self):
        iGCodeParser = GCodeParser()
        gcodeLine = "M104 S150"
        command  = iGCodeParser.parse(gcodeLine)
        self.assertEquals(command, "")
from twisted.trial import unittest
from twisted.internet import defer, reactor
from pollapli.addons.ReprapAddOn_0_0_1_py2_6.reprap.Tools.gcode_parser import GCodeParser
from pollapli.core.hardware.commands import EnableDisableComponents,\
    SetVariableTarget

class TestGCodeParser(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_position_gcode(self):
        gcode_parser = GCodeParser()
        gcode_line = "G0 X1"
        command = gcode_parser.parse(gcode_line)
        self.assertEquals(command, "")

    def test_parse_m104(self):
        gcode_parser = GCodeParser()
        gcode_line = "M104 S150"
        command = gcode_parser.parse(gcode_line)
        self.assertEquals(command, SetVariableTarget(variable="temperature", target_value=150.0))

    def test_parse_m17(self):
        gcode_parser = GCodeParser()
        gcode_line = "M17"
        command = gcode_parser.parse(gcode_line)
        self.assertEquals(command, EnableDisableComponents(component_category="actuator", component_type="stepper", component_on=True))

    def test_parse_m18(self):
        gcode_parser = GCodeParser()
        gcode_line = "M18"
        command = gcode_parser.parse(gcode_line)
        self.assertEquals(command, EnableDisableComponents(component_category="actuator", component_type="stepper", component_on=False))

    def test_parse_m103(self):
        gcode_parser = GCodeParser()
        gcode_line = "M103"
        command = gcode_parser.parse(gcode_line)
        self.assertEquals(command, EnableDisableComponents(component_category="actuator", component_type="extruder", component_on=False))
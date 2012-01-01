from twisted.trial import unittest
from pollapli.core.logic.devices.device import Device
from pollapli.core.logic.devices.device_component import Actuator, Sensor, Tool


class TestDeviceCommands(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_add_actuator(self):
        device = Device(name="TestDevice")
        stepper_motor = Actuator(name="stepper1", category="steppers")
        device.add_child(stepper_motor)

        self.assertEquals(device.children_components, [stepper_motor])

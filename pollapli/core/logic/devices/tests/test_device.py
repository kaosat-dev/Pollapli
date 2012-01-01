from twisted.trial import unittest
from pollapli.core.logic.devices.device import Device
from pollapli.core.logic.devices.device_component import Actuator, Sensor, Tool


class TestDevice(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_add_actuator(self):
        device = Device(name="TestDevice")
        stepper_motor = Actuator(name="stepper1", category="steppers")
        device.add_child(stepper_motor)

        self.assertEquals(device.children_components, [stepper_motor])

    def test_add_sensor(self):
        device = Device(name="TestDevice")
        temperature_sensor = Sensor(name="temperature_sensor", category="temperature")
        device.add_child(temperature_sensor)

        self.assertEquals(device.children_components, [temperature_sensor])

    def test_add_tool(self):
        device = Device(name="TestDevice")
        extruder = Tool(name="extruder1", category="extruder")
        device.add_child(extruder)

        self.assertEquals(device.children_components, [extruder])

    def test_add_tool_elements(self):
        device = Device(name="TestDevice")
        extruder = Tool(name="extruder1", category="extruder")
        stepper = Actuator(name="extruder_1_stepper", category="steppers")
        heater = Actuator(name="extruder_1_heater", category="heater")
        fan = Actuator(name="extruder_1_fan", category="fan")
        temp_sensor = Sensor(name="extruder_1_temperature_sensor", category="temperature")

        extruder.add_children([stepper, heater, fan, temp_sensor])
        device.add_child(extruder)

        self.assertEquals(device.children_components, [extruder])
        self.assertEquals(extruder.children_components, [stepper, heater, fan, temp_sensor])

    def test_get_components_by_category(self):
        device = Device(name="TestDevice")
        extruder = Tool(name="extruder1", category="extruder")
        stepper = Actuator(name="extruder_1_stepper", category="steppers")
        stepper2 = Actuator(name="extruder_1_stepper2", category="steppers")
        heater = Actuator(name="extruder_1_heater", category="heater")
        fan = Actuator(name="extruder_1_fan", category="fan")
        temp_sensor = Sensor(name="extruder_1_temp_sensor", category="temperature")

        extruder.add_children([stepper, stepper2, heater, fan, temp_sensor])
        device.add_child(extruder)

        obs_components = device.get_children_bycategory(category="steppers")
        exp_components = []
        self.assertEquals(obs_components, exp_components)

        obs_components = device.get_children_bycategory(category="extruder")
        exp_components = [extruder]
        self.assertEquals(obs_components, exp_components)

    def test_get_components_by_category_recursive(self):
        device = Device(name="TestDevice")
        extruder = Tool(name="extruder1", category="extruder")
        stepper = Actuator(name="extruder_1_stepper", category="steppers")
        stepper2 = Actuator(name="extruder_1_stepper2", category="steppers")
        heater = Actuator(name="extruder_1_heater", category="heater")
        fan = Actuator(name="extruder_1_fan", category="fan")
        temp_sensor = Sensor(name="extruder_1_temp_sensor", category="temperature")

        extruder.add_children([stepper, stepper2, heater, fan, temp_sensor])
        device.add_child(extruder)

        obs_components = device.get_children_bycategory(category="steppers", recursive=True)
        exp_components = [stepper, stepper2]
        self.assertEquals(obs_components, exp_components)

    def test_get_components_by_type(self):
        device = Device(name="TestDevice")
        extruder = Tool(name="extruder1", category="extruder")
        stepper = Actuator(name="extruder_1_stepper", category="steppers")
        stepper2 = Actuator(name="extruder_1_stepper2", category="steppers")
        heater = Actuator(name="extruder_1_heater", category="heater")
        fan = Actuator(name="extruder_1_fan", category="fan")
        temp_sensor = Sensor(name="TempSensor", category="temperature")

        extruder.add_children([stepper, stepper2, heater, fan])
        device.add_child(extruder)
        device.add_child(temp_sensor)

        obs_components = device.get_children_by_type(type="sensor")
        exp_components = [temp_sensor]
        self.assertEquals(obs_components, exp_components)

    def test_get_components_by_type_recursive(self):
        device = Device(name="TestDevice")
        extruder = Tool(name="extruder1", category="extruder")
        stepper = Actuator(name="extruder_1_stepper", category="steppers")
        stepper2 = Actuator(name="extruder_1_stepper2", category="steppers")
        heater = Actuator(name="extruder_1_heater", category="heater")
        fan = Actuator(name="extruder_1_fan", category="fan")
        temp_sensor = Sensor(name="extruder_1_temp_sensor", category="temperature")

        extruder.add_children([stepper, stepper2, heater, fan, temp_sensor])
        device.add_child(extruder)

        obs_components = device.get_children_by_type(type="Actuator", recursive=True)
        exp_components = [stepper, stepper2, heater, fan]
        self.assertEquals(obs_components, exp_components)

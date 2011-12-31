import abc


class Command(object):
    __metaclass__ = abc.ABCMeta


class EnqueuePosition(Command):
    def __init__(self, target_position, fast_move=False):
        self.target_position = target_position
        self.fast_move = fast_move

class MoveToOrigin(Command):
    pass

class Dwell(Command):
    def __init__(self):
        pass

class SetPositionUnit(Command):
    def __init__(self, unit):
        self.unit = unit

class SetPosition(Command):
    def __init__(self, position):
        self.position = position

class GetPosition(Command):
    def __init__(self):
        pass

class GetCurrentPosition(Command):
    def __init__(self):
        pass

class SetPositioningMode(Command):
    def __init__(self, absolute=False):
        self.positioning_mode = absolute

class AllSteppersSwitch(Command):
    def __init__(self, steppers_on=False):
        self.steppers_on = steppers_on

class AllExtrudersSwitch(Command):
    def __init__(self, extruders_on=False):
        self.extruders_on = extruders_on

class FanSwitch(Command):
    def __init__(self, fan_on=False):
        self.fan_on = fan_on

class CoolerSwitch(Command):
    def __init__(self, cooler_on=False):
        self.cooler_on = cooler_on

class SetExtruderTemperature(Command):
    def __init__(self, index=0, temperature=20):
        self.index = index
        self.temperature = temperature

class SetBedTemperature(Command):
    def __init__(self, temperature):
        self.temperature = temperature

class SetChamberTemperature(Command):
    def __init__(self, temperature):
        self.temperature = temperature

class GetExtruderTemperature(Command):
    def __init__(self, index=0):
        self.index = index

class Stop(Command):
    def __init__(self):
        pass

class GetFirmwareInfo(Command):
    def __init__(self):
        pass


""""""

class EnableDisableComponents(Command):
    """
    :param device: could be more generic? ie target ??
    """
    def __init__(self, device=None, component_category="actuator", component_type="stepper", component_on=False):
        self.device = device
        self.component_category = component_category
        self.component_type = component_type
        self.component_on = component_on

    def __eq__(self, other):
        return (self.__class__ == other.__class__ and 
        self.device == other.device and
        self.component_category == other.component_category and
        self.component_type == other.component_type and
        self.component_on == other.component_on)

    def __ne__(self, other):
        return not self.__eq__(other)

    def run(self):
        self.device.enable_disable_components(self.component_category, self.component_type, self.component_on)


class SetVariableUnit(Command):
    def __init__(self, device=None, variable="position", unit=None):
        self.device = device
        self.variable = variable
        self.unit = unit

    def __eq__(self, other):
        return (self.__class__ == other.__class__ and 
        self.device == other.device and
        self.variable == other.variable and
        self.unit == other.unit)

    def __ne__(self, other):
        return not self.__eq__(other)

    def run(self):
        self.device.set_variable_target(self.variable, self.unit)


class SetVariableTarget(Command):
    def __init__(self, device=None, variable="position", target_value=None):
        self.device = device
        self.variable = variable
        self.target_value = target_value

    def __eq__(self, other):
        return (self.__class__ == other.__class__ and 
        self.device == other.device and
        self.variable == other.variable and
        self.target_value == other.target_value)

    def __ne__(self, other):
        return not self.__eq__(other)

    def run(self):
        self.device.set_variable_target(self.variable, self.target_value)

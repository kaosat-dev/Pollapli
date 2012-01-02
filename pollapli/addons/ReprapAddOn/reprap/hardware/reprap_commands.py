from pollapli.core.hardware.commands import Command


class EnqueuePosition(Command):
    """Enqueues a (5d) position"""
    def __init__(self, device=None, target_position=None, rapid=False):
        Command.__init__(self, device)
        self.target_position = target_position
        self.rapid = rapid

    def __eq__(self, other):
        return (self.__class__ == other.__class__ and
                self.target_position == other.target_position and
                self.rapid == other.rapid)

    def __ne__(self, other):
        return not self.__eq__(other)

    def run(self):
        return self.device.enqueue_position(self.target_position, self.rapid)


class MoveToOrigin(Command):
    """Moves to  origin"""
    def __init__(self, device=None):
        Command.__init__(self, device)

    def __eq__(self, other):
        return (self.__class__ == other.__class__)

    def __ne__(self, other):
        return not self.__eq__(other)

    def run(self):
        return self.device.move_to_origin()


class Dwell(Command):
    """"""
    def __init__(self, device=None):
        Command.__init__(self, device)

    def __eq__(self, other):
        return (self.__class__ == other.__class__)

    def __ne__(self, other):
        return not self.__eq__(other)

    def run(self):
        return self.device.dwell()


class GetPosition(Command):
    """Get current position"""
    def __init__(self, device=None):
        Command.__init__(self, device)

    def __eq__(self, other):
        return (self.__class__ == other.__class__)

    def __ne__(self, other):
        return not self.__eq__(other)

    def run(self):
        return self.device.get_position()


class SetPosition(Command):
    """Set current position"""
    def __init__(self, device=None, position=None):
        Command.__init__(self, device)
        self.position = position

    def __eq__(self, other):
        return (self.__class__ == other.__class__ and
                self.position == other.position)

    def __ne__(self, other):
        return not self.__eq__(other)

    def run(self):
        return self.device.set_position(self.position)


class SetPositionUnit(Command):
    """Set current positioning unit"""
    def __init__(self, device=None, unit="mm"):
        Command.__init__(self, device)
        self.unit = unit

    def __eq__(self, other):
        return (self.__class__ == other.__class__ and
                self.unit == other.unit)

    def __ne__(self, other):
        return not self.__eq__(other)

    def run(self):
        return self.device.set_unit(self.unit)


class SetPositioningMode(Command):
    """Set current positioning mode"""
    def __init__(self, device=None, absolute=False):
        Command.__init__(self, device)
        self.positioning_mode = absolute

    def __eq__(self, other):
        return (self.__class__ == other.__class__ and
                self.positioning_mode == other.positioning_mode)

    def __ne__(self, other):
        return not self.__eq__(other)

    def run(self):
        return self.device.set_positioning_mode(self.positioning_mode)


class SetExtruderTemperature(Command):
    """Set extruder temperature"""
    def __init__(self, device=None, index=0, temperature=20):
        Command.__init__(self, device)
        self.index = index
        self.temperature = temperature

    def __eq__(self, other):
        return (self.__class__ == other.__class__ and
                self.index == other.index and
                self.temperature == other.temperature)

    def __ne__(self, other):
        return not self.__eq__(other)

    def run(self):
        return self.device.set_extruder_temperature(self.index, self.temperature)


class GetExtruderTemperature(Command):
    """Set extruder temperature"""
    def __init__(self, device=None, index=0):
        Command.__init__(self, device)
        self.index = index

    def __eq__(self, other):
        return (self.__class__ == other.__class__ and
                self.index == other.index)

    def __ne__(self, other):
        return not self.__eq__(other)

    def run(self):
        return self.device.get_extruder_temperature(self.index)


class SetBedTemperature(Command):
    """Set bed temperature"""
    def __init__(self, device=None, temperature=20):
        Command.__init__(self, device)
        self.temperature = temperature

    def __eq__(self, other):
        return (self.__class__ == other.__class__ and
                self.temperature == other.temperature)

    def __ne__(self, other):
        return not self.__eq__(other)

    def run(self):
        return self.device.set_bed_temperature(self.temperature)


class GetBedTemperature(Command):
    """Set extruder temperature"""
    def __init__(self, device=None):
        Command.__init__(self, device)

    def __eq__(self, other):
        return (self.__class__ == other.__class__)

    def __ne__(self, other):
        return not self.__eq__(other)

    def run(self):
        return self.device.get_bed_temperature()


class SetChamberTemperature(Command):
    """Set chamber temperature"""
    def __init__(self, device=None, temperature=20):
        Command.__init__(self, device)
        self.temperature = temperature

    def __eq__(self, other):
        return (self.__class__ == other.__class__ and
                self.temperature == other.temperature)

    def __ne__(self, other):
        return not self.__eq__(other)

    def run(self):
        return self.device.set_chamber_temperature(self.temperature)


class GetChamberTemperature(Command):
    """Set chamber temperature"""
    def __init__(self, device=None):
        Command.__init__(self, device)

    def __eq__(self, other):
        return (self.__class__ == other.__class__)

    def __ne__(self, other):
        return not self.__eq__(other)

    def run(self):
        return self.device.get_chamber_temperature()


class FanSwitch(Command):
    """Set cooler on/off """
    def __init__(self, device=None, fan_on=False):
        Command.__init__(self, device)
        self.fan_on = fan_on

    def __eq__(self, other):
        return (self.__class__ == other.__class__ and
                self.fan_on == other.fan_on)

    def __ne__(self, other):
        return not self.__eq__(other)

    def run(self):
        return self.device.switch_cooler(self.fan_on)


class CoolerSwitch(Command):
    """Set fan on/off """
    def __init__(self, device=None, cooler_on=False):
        Command.__init__(self, device)
        self.cooler_on = cooler_on

    def __eq__(self, other):
        return (self.__class__ == other.__class__ and
                self.cooler_on == other.cooler_on)

    def __ne__(self, other):
        return not self.__eq__(other)

    def run(self):
        return self.device.switch_fan(self.cooler_on)


class AllExtrudersSwitch(Command):
    """Set all extruders on/off """
    def __init__(self, device=None, extruders_on=False):
        Command.__init__(self, device)
        self.extruders_on = extruders_on

    def __eq__(self, other):
        return (self.__class__ == other.__class__ and
                self.extruders_on == other.extruders_on)

    def __ne__(self, other):
        return not self.__eq__(other)

    def run(self):
        return self.device.switch_all_extruders(self.extruders_on)


class AllSteppersSwitch(Command):
    """Set all steppers on/off """
    def __init__(self, device=None, steppers_on=False):
        Command.__init__(self, device)
        self.steppers_on = steppers_on

    def __eq__(self, other):
        return (self.__class__ == other.__class__ and
                self.steppers_on == other.steppers_on)

    def __ne__(self, other):
        return not self.__eq__(other)

    def run(self):
        return self.device.switch_all_extruders(self.steppers_on)

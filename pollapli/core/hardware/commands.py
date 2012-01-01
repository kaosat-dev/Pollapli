from twisted.internet import defer


class Command(object):
    def __init__(self, device=None):
        self.device = device
        self.deferred = defer.Deferred()

    def run(self):
        """Run the command on the device, should return a deferred"""
        raise NotImplementedError()


class HelloWorld(Command):
    """Just a dummy command"""
    def __init__(self, device=None):
        Command.__init__(self, device)

    def __eq__(self, other):
        return (self.__class__ == other.__class__)

    def __ne__(self, other):
        return not self.__eq__(other)

    def run(self):
        return self.device.hello_world()


class GetFirmwareInfo(Command):
    """Returns the firmware info"""
    def __init__(self, device=None):
        Command.__init__(self, device)

    def __eq__(self, other):
        return (self.__class__ == other.__class__)

    def __ne__(self, other):
        return not self.__eq__(other)

    def run(self):
        return self.device.get_firmware_info()


class GetHardwareId(Command):
    """Returns  the hardware id"""
    def __init__(self, device=None):
        Command.__init__(self, device)

    def __eq__(self, other):
        return (self.__class__ == other.__class__)

    def __ne__(self, other):
        return not self.__eq__(other)

    def run(self):
        return self.device.get_hardware_id()


class Stop(Command):
    """Stops the device"""
    def __init__(self, device=None):
        Command.__init__(self, device)

    def __eq__(self, other):
        return (self.__class__ == other.__class__)

    def __ne__(self, other):
        return not self.__eq__(other)

    def run(self):
        return self.device.stop()


"""
###########################################################################
The following are not yet finished generic commands
"""


class EnableDisableComponents(Command):
    """
    :param device: could be more generic? ie target ??
    """
    def __init__(self, device=None, component_category="actuator", component_type="stepper", component_on=False):
        Command.__init__(self, device)
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
        Command.__init__(self, device)
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
        Command.__init__(self, device)
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

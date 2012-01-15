"""All classes related to device components:
Actuators, sensors, variables etc"""

import logging
from twisted.python import log
from pollapli.core.base.base_component import BaseComponent

class BaseDeviceComponent(BaseComponent):
    """Base class for device components"""
    def __init__(self, parent=None, name="", description=""):
        BaseComponent.__init__(self, parent)
        self.name = name
        self.description = description
        self.children_components = []

    def add_child(self, child=None):
        """
        add a child element to the component
        :param child: the child to add
        """
        if child is None:
            raise Exception("No child specified")
        child.parent = self
        self.children_components.append(child)

    def add_children(self, children=None):
        """
        add children elements to the component
        :param children : a list of children to add
        """
        if children is None:
            raise Exception("No children specified")
        for child in children:
            child.parent = self
            self.children_components.append(child)

    def remove_child(self, child=None):
        """
        remove a child element from the component
        :param child: the child to remove
        """
        if child is None:
            raise Exception("No child specified")
        child.parent = None
        self.children_components.remove(child)

    def clear_children(self):
        """remove all children"""
        for child in self.children_components:
            self.remove_child(child)

    def get_children_bycategory(self, category=None, recursive=False):
        """
        return a list of children , filtered by category
        :param category: the category to look for
        :param recursive: look for components with the given category
        in sub elements as well
        """
        if category is None:
            raise Exception("No category specified")
        result = []
        for child in self.children_components:
            if child.__class__.__name__ != Variable:
                if child.category == category:
                    result.append(child)
                if recursive:
                    result.extend(child.get_children_bycategory(category, True))
        return result

    def get_children_by_type(self, type=None, recursive=False):
        """
        return a list of children , filtered by type (class name)
        :param type: the type to look for
        :param recursive: look for components with the given type
        in sub elements as well
        """
        result = []
        for child in self.children_components:
            if child.__class__.__name__.lower() == type.lower():
                result.append(child)
            if recursive:
                result.extend(child.get_children_by_type(type, True))
        return result

    def link_component_to_variable(self, component, variable, var_channel=None):
        pass


class Tool(BaseDeviceComponent):
    """A component representing tools : these usually act as containers"""
    def __init__(self, parent=None, name="", description="", category="generic"):
        BaseDeviceComponent.__init__(self, parent, name, description)
        self.category = category


class ConcreteDeviceComponent(BaseDeviceComponent):
    """Base class for real/physical components: sensor, actuators etc"""
    def __init__(self, parent=None, name="", description="", category=None):
        BaseDeviceComponent.__init__(self, parent, name, description)
        self.category = category
        self.linked_variable = None
        self.linked_variable_channel = None


class Sensor(ConcreteDeviceComponent):
    """Abstraction class for sensors"""
    def __init__(self, parent=None, name="", description="", category=""):
        ConcreteDeviceComponent.__init__(self, parent, name, description, category)


class Actuator(ConcreteDeviceComponent):
    """Abstraction class for actuators"""
    def __init__(self, parent=None, name="", description="", category=""):
        ConcreteDeviceComponent.__init__(self, parent, name, description, category)


class VariableOld(BaseDeviceComponent):
    """This class represents a physical variable that can be controlled
    by a device"""
    def __init__(self, parent=None, name="", description="", value=None, defaultValue=None, max_rateofchange=None, variable_type=None, unit=""):
        BaseDeviceComponent.__init__(self, parent, name, description)
        self.value = value
        self.defaultValue = defaultValue or value
        self.targetValue = None
        self.max_rateofchange = max_rateofchange
        self.variable_type = variable_type
        self.unit = unit

    def set(self, value, relative=False, params=None, sender=None):
        """ setting is dependent on the type of  variable
        This is a delayed operation: set just initiates the chain of events
        leading to an actual update
        it calls the driver set method + this variables type :ie  for
        a position: set_name_position
        all variable types need to support adding
        """
        if relative:
            self.targetValue += value
        else:
            self.targetValue = value
        #send command to driver

    def get(self):
        pass

    def reset(self, value=None, to_default=True):
        """reset a variable to a value or default value"""
        if value is not None:
            self.value = value
        if to_default:
            self.value = self.defaultValue


class Variable(BaseDeviceComponent):
    """This class represents a physical variable that can be controlled
    by a device"""
    def __init__(self, parent=None, name="", description="", value_data=None, rateofchange_data=None, variable_type=None, unit=""):
        """
        :param value_data: tupple of value, default value
        :param variation_data : tupple of rate of change, max rate of change
        """
        BaseDeviceComponent.__init__(self, parent, name, description)
        self.value, self.default_value, self.min_value, self.max_value = value_data
        self.rate_of_change, self.min_rate_of_change, self.max_rate_of_change = rateofchange_data
        self.target_value = None
        self.variable_type = variable_type
        self.unit = unit

    def set_variable(self, value, relative=False, params=None):
        """ setting is dependent on the type of  variable
        This is a delayed operation: set just initiates the chain of events
        leading to an actual update
        it calls the driver set method + this variables type :ie  for
        a position: set_name_position
        all variable types need to support adding
        """
        if relative:
            self.target_value += value
        else:
            self.target_value = value
        #send command to driver

    def get_variable(self):
        pass

    def reset(self, value=None, home=True):
        """reset a variable to a value or default value"""
        if value is not None:
            self.value = value
        if home:
            self.value = self.default_value

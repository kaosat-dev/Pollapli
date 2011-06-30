from zope.interface import Interface, Attribute

class IConnector(Interface):
    """
    Connector class , encapsulating a driver and its connection
    """

class Connector(object):
    """
    Connector class , encapsulating a driver and its connection
    """
    def __init__(self):
        self.driver=None
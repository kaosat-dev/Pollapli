
class DeviceComponent(object):
    """A sub element of a node : such as actor, sensor etc """
    def __init__(self, componentType="dummy",name="",tool="",boundVariable=None,variableChannel=None):
        self.name=name
        self.componentType=componentType
        self.boundVariable=boundVariable #what variable is it bound to
        self.channel=variableChannel
        self.driverEndpoint=None
        
    def set_endPoint(self,endPoint):
        self.driverEndpoint=endPoint
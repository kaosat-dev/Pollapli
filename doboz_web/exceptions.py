import exceptions

class EnvironmentAlreadyExists(Exception):
  pass

class EnvironmentNotFound(Exception):
    pass

class UnknownNodeType(Exception):
  pass

class NodeNotFound(Exception):
    pass

class NoDriverSet(Exception):
    pass

class UnknownDriver(Exception):
    pass

class DeviceHandshakeMismatch(Exception):
    pass
class DeviceIdMismatch(Exception):
    pass
class NoAvailablePort(Exception):
    pass

class UnknownTask(Exception):
    pass

class UnknownUpdate(Exception):
    pass

class InvalidFile(Exception):
    pass

""""""""""""""""""""""""""""""""""""
"""rest handler exceptions"""
class ParameterParseException(Exception):
    pass

class UnhandledContentTypeException(Exception):
    pass

class JsonPayloadGenerationException(Exception):
    pass
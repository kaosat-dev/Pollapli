import exceptions

class EnvironmentAlreadyExists(Exception):
    pass

class EnvironmentNotFound(Exception):
    pass

class UnknownDeviceType(Exception):
    pass

class DeviceNotFound(Exception):
    pass

class NoDriverSet(Exception):
    pass

class UnknownDriver(Exception):
    pass

class DeviceHandshakeMismatch(Exception):
    pass
class DeviceIdMismatch(Exception):
    pass
class DeviceNotConnected(Exception):
    pass
class NoAvailablePort(Exception):
    pass

class TaskNotFound(Exception):
    pass
class UnknownTask(Exception):
    pass
class UnknownUpdate(Exception):
    pass
class UpdateNotFound(Exception):
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
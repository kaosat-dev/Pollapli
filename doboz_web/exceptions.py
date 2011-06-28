import exceptions

class EnvironmentAlreadyExists(Exception):
  pass

class EnvironmentNotFound(Exception):
    pass

class UnknownNodeType(Exception):
  pass

class NodeNotFound(Exception):
    pass

class NoConnectorSet(Exception):
    pass

class UnknownConnector(Exception):
    pass

class UnknownDriver(Exception):
    pass

""""""""""""""""""""""""""""""""""""
"""rest handler exceptions"""
class ParameterParseException(Exception):
    pass

class UnhandledContentTypeException(Exception):
    pass

class JsonPayloadGenerationException(Exception):
    pass
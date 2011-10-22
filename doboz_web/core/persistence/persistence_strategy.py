import abc 

class PersistenceStrategy(object):
    """this class defines , what goes where ( different objects into different dbs)"""
    __metaclass__ = abc.ABCMeta
import abc

class NodeDao(object):
    __metaclass__ = abc.ABCMeta
    
    @abc.abstractmethod
    def load_node(self,*args,**kwargs):
        """Retrieve data from node object."""
        return
    
    @abc.abstractmethod
    def save_node(self, node):
        """Save the node object ."""
        return
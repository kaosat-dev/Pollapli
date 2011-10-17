from doboz_web.core.persistance.dao_base.node_dao import NodeDao
from doboz_web.core.logic.components.nodes.node import Node


class NodeSqliteDao(NodeDao):
    
    def load_node(self,*args,**kwargs):
        """Retrieve data from node object."""
        return
    
    def save_node(self, node):
        """Save the node object ."""
        return
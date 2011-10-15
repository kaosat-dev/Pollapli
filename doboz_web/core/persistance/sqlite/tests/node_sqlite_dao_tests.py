from twisted.trial import unittest
from doboz_web.run import *
from doboz_web.core.persistance.sqlite.node_sqlite_dao import NodeSqliteDao
from doboz_web.core.logic.components.nodes.node import Node

#TODO : replace mutual dependency of tests with manual sqlite inserts/selects

class NodeSqliteDaoTests(unittest.TestCase):
    def setUp(self):
        configure_all() 
        self.nodeSqliteDao=nodeSqliteDao()
        
    def tearDown(self):
        pass
    
    def test_save_node(self):
        exp = Node(name="test",description="test")
        self.nodeSqliteDao.save_node(input)
        obs = self.nodeSqliteDao.load_node()
        self.assertEquals(obs,exp)
        
    def test_load_nodebyid(self):    
        input = Node(name="test",description="test")
        self.nodeSqliteDao.save_node(input)
        exp = input
        obs = self.nodeSqliteDao.load_node(id == 1)
        self.assertEquals(obs,exp)

    def test_load_nodes(self):
        input = [Node(name="node1"),Node(name="node2")]
        exp = input
        obs = self.nodeSqliteDao.load_all_nodes()
        self.assertEquals(obs,exp)
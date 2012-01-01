import unittest
from urllib2 import*
from restclient import Resource

  
class TestNodes(unittest.TestCase):
    def setUp(self):
       self.client=Resource('http://127.0.0.1:8000')
       response=self.client.put('/environments',headers={'Content-Type': 'application/json'},payload='{"name":"test"}')
       self.failUnlessEqual(200, self.client.status)
    
    def test_NodeCreate(self):    
        response=self.client.post('/environments/0/nodes',headers={'Content-Type': 'application/json'},payload='{"name":"testNode","type":"reprap"}')
        self.failUnlessEqual(200, self.client.status)
        
    def test_NodesRead(self):
        self.client.get('/environments/0/nodes',headers={'Content-Type': 'application/json'})
        self.failUnlessEqual(200, self.client.status)
        
    def test_NodeUpdate(self):
        pass
    def test_NodesDelete(self):
        self.client.delete('/environments/0/nodes',headers={'Content-Type': 'application/json'})
        self.failUnlessEqual(200, self.client.status)
            
    def tearDown(self):
        self.client.delete('/environments',headers={'Content-Type': 'application/json'})

class TestNodeConnector(unittest.TestCase):
    def setUp(self):
       self.client=Resource('http://127.0.0.1:8000')
       self.client.post('/environments',headers={'Content-Type': 'application/json'},payload='{"name":"test"}')
       self.client.post('/environments/0/nodes',headers={'Content-Type': 'application/json'},payload='{"name":"testNode","type":"reprap"}')
    
    def test_ConnectorCreate(self):          
        self.client.put('/environments/0/nodes/0/connector',headers={'Content-Type': 'application/json'},payload='{"driverType":"teacup","driverParams":{"speed":115200}}')
        self.failUnlessEqual(200, self.client.status)
         
    def test_ConnectorRead(self):
        self.client.get('/environments/0/nodes/0/connector',headers={'Content-Type': 'application/json'})
        self.failUnlessEqual(200, self.client.status)
        
    def test_ConnectorUpdate(self):
        self.client.put('/environments/0/nodes/0/connector',headers={'Content-Type': 'application/json'},payload='{"driverType":"teacup","driverParams":{"speed":115200}}')
        self.failUnlessEqual(200, self.client.status)
        
    def test_ConnectorDelete(self):
        self.client.delete('/environments/0/nodes/0/connector',headers={'Content-Type': 'application/json'})
        self.failUnlessEqual(200, self.client.status)
        
    def test_ConnectorStatusUpdate(self):
        self.client.put('/environments/0/nodes/0/connector',headers={'Content-Type': 'application/json'},payload='{"driverType":"teacup","driverParams":{"speed":115200}}')
        self.failUnlessEqual(200, self.client.status)
        
        self.client.post('/environments/0/nodes/0/connector/status',headers={'Content-Type': 'application/json'},payload='{"connected":"True"}')
        self.failUnlessEqual(200, self.client.status)
        
    def tearDown(self):
        self.client.delete('/environments',headers={'Content-Type': 'application/json'})

import unittest
from urllib2 import*
from restclient import Resource

  
class TestEnvironments(unittest.TestCase):
    def setUp(self):
       self.client=Resource('http://127.0.0.1:8000')
    
    def test_EnvironmentCreate(self):
        response=self.client.put('/environments',headers={'Content-Type': 'application/json'},payload='{"name":"test"}')
        self.failUnlessEqual(200, self.client.status)
        
    def test_EnvironmenstRead(self):
        self.client.get('/environments',headers={'Content-Type': 'application/json'})
        self.failUnlessEqual(200, self.client.status)
        try:
            self.client.get('/environments',headers={'Content-Type': 'application/xml'})
        except:
            pass
        self.failUnlessEqual(500, self.client.status)
        
        self.client.put('/environments',headers={'Content-Type': 'application/json'},payload='{"name":"test"}')
        response=self.client.get('/environments',headers={'Content-Type': 'application/json'})
        self.failUnlessEqual('{"Environments":["test"]}',response)
        
    def test_EnvironmentUpdate(self):
        pass
    def test_EnvironmentsDelete(self):
        self.client.delete('/environments',headers={'Content-Type': 'application/json'})
        self.failUnlessEqual(200, self.client.status)
        
    def tearDown(self):
        self.client.delete('/environments',headers={'Content-Type': 'application/json'})

  
import unittest
from urllib2 import*
from restclient import Resource

def helper():
    """
    cheap hack for now for easier testing
    """
    client=Resource('http://127.0.0.1:8000')
    try:
        client.post('rest/environments',headers={'Content-Type': 'application/pollapli.environmentsList+json'},payload='{"name":"fablab","status":"frozen","description":"blabla"}')
    except:
        pass
    try:
        client.post('rest/environments/0/nodes',headers={'Content-Type': 'application/pollapli.nodesList+json'},payload='{"name":"testNode","type":"node","description":"just a test node"}')
    except:
        pass
#    try:
#        client.post('/environments/0/nodes/0/tasks',headers={'Content-Type': 'application/json'},payload='{"name":"testTask","type":"print","taskParams":{"filePath":"test.gcode"}}')
#    except:
#        pass

helper()


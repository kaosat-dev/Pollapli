import unittest
from urllib2 import*
from restclient import Resource

def helper():
    """
    cheap hack for now for easier testing
    """
    client=Resource('http://127.0.0.1:8000')
    try:
        client.post('rest/environments',headers={'Content-Type': 'application/pollapli.environmentList+json'},payload='{"name":"home","status":"frozen","description":"blabla"}')
    except:
        pass
    try:
        client.post('rest/environments/1/nodes',headers={'Content-Type': 'application/pollapli.nodeList+json'},payload='{"name":"testNode","type":"reprap","description":"just a reprap node"}')
    except:
        pass
    try:
        client.post('rest/environments/1/nodes',headers={'Content-Type': 'application/pollapli.nodeList+json'},payload='{"name":"testNode","type":"dummy","description":"just a test node"}')
    except:
        pass
    try:
        pass
        #client.post('rest/environments/1/nodes/1/connector',headers={'Content-Type': 'application/pollapli.connector+json'},payload='{"driverType":"teacupdriver","driverParams":{"speed":115200}}')
    except:
        pass
#    try:
#        client.post('/environments/0/nodes/0/tasks',headers={'Content-Type': 'application/json'},payload='{"name":"testTask","type":"print","taskParams":{"filePath":"test.gcode"}}')
#    except:
#        pass

helper()


import unittest
from urllib2 import*
from restclient import Resource

def helper():
    """
    cheap hack for now for easier testing
    """
    client=Resource('http://127.0.0.1:8000')
    try:
        client.post('/environments',headers={'Content-Type': 'application/json'},payload='{"name":"test"}')
    except:
        pass
    try:
        client.post('/environments/0/nodes',headers={'Content-Type': 'application/json'},payload='{"name":"testNode","type":"reprap"}')
    except:
        pass
    try:
        client.post('/environments/0/nodes/0/tasks',headers={'Content-Type': 'application/json'},payload='{"name":"testTask","type":"print"}')
    except:
        pass

helper()


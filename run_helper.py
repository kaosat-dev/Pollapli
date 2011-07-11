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
        client.post('rest/environments/1/nodes',headers={'Content-Type': 'application/pollapli.nodeList+json'},payload='{"name":"reprap1","type":"reprap","description":"just a reprap node"}')
    except:
        pass
    try:
        client.post('rest/environments/1/nodes',headers={'Content-Type': 'application/pollapli.nodeList+json'},payload='{"name":"reprap2","type":"reprap","description":"just a reprap node"}')
    except:
        pass
    try:
        client.post('rest/environments/1/nodes',headers={'Content-Type': 'application/pollapli.nodeList+json'},payload='{"name":"testNode","type":"dummy","description":"just a test node"}')
    except:
        pass
    try:
        client.post('rest/environments/1/nodes/1/driver',headers={'Content-Type': 'application/pollapli.driver+json'},payload='{"driverType":"teacupdriver","driverParams":{"speed":115200}}')
    except:
        pass
    try:
        client.post('rest/environments/1/nodes/2/driver',headers={'Content-Type': 'application/pollapli.driver+json'},payload='{"driverType":"arduinoexampledriver","driverParams":{"speed":115200}}')
    except:
        pass
    try:
        client.post('rest/environments/1/nodes/1/tasks',headers={'Content-Type': 'application/pollapli.taskList+json'},payload='{"name":"testTask","description":"a task for printing 3D models","type":"print","params":{"filepath":"toto.gcode"}}')
    except Exception as inst:
        print("failed to add task",str(inst))

helper()


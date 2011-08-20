import unittest
from urllib2 import*
import httplib2
#from restclient import Resource


class Resource(object):
    def __init__(self,url):
        self.url=url
    def post(self,url,headers,payload):
        h = httplib2.Http(".cache")
        h.request(self.url+"/"+url, "POST", body=payload, headers=headers)


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
        client.post('rest/environments/1/nodes',headers={'Content-Type': 'application/pollapli.nodeList+json'},payload='{"name":"hydroduino test","type":"hydroduino","description":"just a garden node"}')
    except:
        pass
    try:
        client.post('rest/environments/1/nodes',headers={'Content-Type': 'application/pollapli.nodeList+json'},payload='{"name":"repraptest","type":"reprap","description":"just a reprap node"}')
    except:
        pass
    try:
        client.post('rest/environments/1/nodes',headers={'Content-Type': 'application/pollapli.nodeList+json'},payload='{"name":"testNode","type":"reprap","description":"just a test node"}')
    except:
        pass
    try:
        client.post('rest/environments/1/nodes/1/driver',headers={'Content-Type': 'application/pollapli.driver+json'},payload='{"driverType":"hydroduinodriver","driverParams":{"speed":115200}}')
    except:
        pass
    try:
        client.post('rest/environments/1/nodes/2/driver',headers={'Content-Type': 'application/pollapli.driver+json'},payload='{"driverType":"virtualdevicedriver","driverParams":{"speed":19200}}')
    except:
        pass
    try:
        pass
        #client.post('rest/environments/1/nodes/1/tasks',headers={'Content-Type': 'application/pollapli.taskList+json'},payload='{"name":"testTask","description":"a task for printing 3D models","taskType":"print","params":{"filepath":"test.gcode"}}')
    except Exception as inst:
        print("failed to add task",str(inst))


#http://127.0.0.1:8000/rest/config/events  Content-Type: application/pollapli.event+json
helper()


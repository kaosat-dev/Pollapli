from zope.interface import Interface, Attribute,implements
from twisted.plugin import IPlugin
from doboz_web import idoboz_web 
from zope.interface import classProvides

class TestPlugin3(object):
    classProvides(IPlugin, idoboz_web.ITestPlugin)
    def __init__(self):
        print("here in test plugin")
    def doAThing(self,data):
        print("data in plugin",data)
        
#toto=TestPlugin3()
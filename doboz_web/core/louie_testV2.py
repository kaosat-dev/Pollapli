from louie import dispatcher,error,Any,All,Anonymous,plugin

from louie.plugin import TwistedDispatchPlugin 
import louie
from twisted.python import log,failure
import logging

class TestChannel(object):
    def __init__(self):
        self.id=0
        self.chanName="toto"
    
    
class SignalTest(object):
    plugin.install_plugin(TwistedDispatchPlugin())
    def __init__(self,name="",channels=[]):
        self.name=name
        for channel in channels:
            louie.connect(self, signal=channel, sender=Any, weak=True)
            
    def __call__(self,signal=None,sender=None,*args,**kwargs):
        #log.msg(self.name, "recieved signal", kwargs.get("signal"),"with data",kwargs.get("data"),"from ",kwargs.get("sender"),logLevel=logging.CRITICAL)
        log.msg(self.name, "recieved signal with data",kwargs.get("data"),logLevel=logging.CRITICAL)
        print("sig",signal,"sender",sender)
        print("kwargs",kwargs)
    def send_message(self,channel=None,message={},*args,**kwargs):
        err=louie.send(channel or "dump",self,**message)
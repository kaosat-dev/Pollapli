from louie import dispatcher,error,Any,All,Anonymous,plugin
from louie.plugin import TwistedDispatchPlugin 
import louie
from twisted.python import log,failure
import logging

class TestChannel(object):
    def __init__(self):
        self.id=0
        self.chanName="toto"
    
class SignalHander(object):
    plugin.install_plugin(TwistedDispatchPlugin())
    def __init__(self,name="",recieversInfo=[]):
        self.name=name
        self.callables=[]
        self.thingy={}
        for signal,sender,handlers in recieversInfo:
            self.thingy[(signal,sender)]=handlers
            print("thingy",self.thingy)
            louie.connect(self, signal=signal, sender=sender, weak=True)
            
    def __call__(self,signal=None,sender=None,*args,**kwargs):
        log.msg(self.name, " recieved ",signal," from ",sender,logLevel=logging.CRITICAL)
        try:
            [callable(**kwargs) for callable in self.thingy[signal,sender]]
        except Exception as inst:
            print("error",inst)
    def _get_handler(self,signal,sender):
        pass
        
    def send_message(self,channel=None,message={},*args,**kwargs):
        err=louie.send(channel or "dump", self,**message)

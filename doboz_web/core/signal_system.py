from louie import dispatcher,error,Any,All,Anonymous,plugin
from louie.plugin import TwistedDispatchPlugin 
import louie
from twisted.python import log,failure
import logging

class SignalChannel(object):
    def __init__(self,channelName):
        pass
class SignalHander(object):
    plugin.install_plugin(TwistedDispatchPlugin())
    def __init__(self,channel="",recieversInfo=[]):
        self.channel=channel
        self.truc=SignalChannel(self.channel)
#        self.callables=[]
#        self.thingy={}
#        if recieversInfo:
#            for signal,sender,handlers in recieversInfo:
#                self.thingy[(signal,sender)]=handlers
#                #print("thingy",self.thingy)
#                louie.connect(self, signal=signal, sender=Any, weak=True)
#        else:
#            louie.connect(self,signal=All,sender=None,weak=True)
        #louie.connect(self,signal=self.truc,sender=Any,weak=True)
        
    def add_handler(self,handler=None,signal="",sender=Any):
        louie.connect(handler or self,signal=self.channel+'.'+signal,sender=sender,weak=True)
        
    def __call__(self,signal=None,sender=None,*args,**kwargs):
        #log.msg(self.channel, " recieved ",signal," from ",sender, "with data" ,args,kwargs,logLevel=logging.CRITICAL)
        realsignal=signal
        try:
            realsignal=signal.split('.')
            realsignal=realsignal[len(realsignal)-1]
        except:
            realsignal=signal
        log.msg(self.channel, " recieved ",realsignal," from ",sender, "with data" ,args,kwargs,logLevel=logging.CRITICAL)
        
        try:
            [callable(**kwargs) for callable in self.thingy[signal,sender]]
        except Exception as inst:
            pass#print("error",inst)
    def _get_handler(self,signal,sender):
        pass
    def send_message(self,signal=None,message={},*args,**kwargs):
        if message:
            err=louie.send(self.channel+'.'+signal or "dump", self.channel,**message)
    
    def send_message_old(self,sender=None,signal=None,message={},*args,**kwargs):
        if message:
            err=louie.send(self.channel+signal or "dump", sender or self,**message)

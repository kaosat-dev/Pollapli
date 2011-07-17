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
        
    def add_handler(self,handler=None,signal="",sender=Any):
        louie.connect(handler or self,signal=self.channel+'.'+signal,sender=sender,weak=True)
    def add_handler2(self,handler=None,signal="",sender=Any):
        louie.connect(handler or self,signal=signal,sender=sender,weak=True)
        
    def _get_handler(self,signal,sender):
        pass
    
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
    
    def send_message(self,signal=None,message={},out=False,*args,**kwargs):
        if message:
            realsig=signal
            if not out:
                realsig=self.channel+'.'+signal
                
            #log.msg("Sending message",realsig, "from", self.channel,"with data",message,logLevel=logging.CRITICAL)
            err=louie.send(realsig, self.channel,**message)
    
    

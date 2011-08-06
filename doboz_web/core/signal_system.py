from louie import dispatcher,error,Any,All,Anonymous,plugin
from louie.plugin import TwistedDispatchPlugin 
import louie
from twisted.python import log,failure
import logging

class SignalChannel(object):
    def __init__(self,channelName):
        pass
class Command(object):
    def __init__(self,sender=None):
        pass
    
class SignalHander(object):
    plugin.install_plugin(TwistedDispatchPlugin())
    def __init__(self,channel="",recieversInfo=[]):
        self.channel=channel
        log.msg("setting up signal handler on channel",self.channel,logLevel=logging.DEBUG)

        
    def add_handler_old(self,handler=None,signal="",sender=Any):
        louie.connect(handler or self,signal=self.channel+'.'+signal,sender=sender,weak=True)
    def add_handler_old2(self,handler=None,signal="",sender=Any):
        louie.connect(handler or self,signal=signal or All,sender=sender,weak=True)
    
    def add_handler(self,handler=None,signal=None,channel="global"):
        """sets up listing to a channel"""
        
        louie.connect(handler or self,signal=signal or All,sender=channel,weak=True)
        
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
    
    def send_message_old(self,sender=None,signal=None,message=None,*args,**kwargs):
        log.msg("sending message ",message," from ",sender, "with signal" ,signal,logLevel=logging.DEBUG)

        realsig=self.channel+'.'+signal
             
        if sender is None:
            err=louie.send(realsig, self.channel,**message or {})
        else:
            err=louie.send(realsig, sender,**message or {})
            
    def send_message(self,message="",sender=None,params=None,*args,**kwargs):
        realParams={"data":params,"realsender":sender}
        
        log.msg("sending message ",message," from ",sender, "to channel" ,self.channel,"with params",realParams,logLevel=logging.DEBUG)

        
        err=louie.send(message, self.channel,**realParams )
        
        
    
from louie import dispatcher,error,Any,All,Anonymous,plugin
from louie.plugin import TwistedDispatchPlugin 
import louie
import time
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

    
    def add_handler(self,handler=None,signal=None,channel="global"):
        """sets up listing to a channel"""
        louie.connect(handler or self,signal=signal or All,sender=channel,weak=True)
        
    def _get_handler(self,signal,sender):
        pass
    
    def __call__(self,signal=None,sender=None,*args,**kwargs):
       
        log.msg(self.channel, " recieved ",signal," from ",sender, "with data" ,args,kwargs,logLevel=logging.CRITICAL)
    
            
    def send_message(self,message="",sender=None,params=None,*args,**kwargs):
        realParams={"data":params,"realsender":sender,"time":time.time()}
        log.msg("sending message ",message," from ",sender, "to channel" ,self.channel,"with params",realParams,logLevel=logging.DEBUG)
        err=louie.send(message, self.channel,**realParams )
        
        
    
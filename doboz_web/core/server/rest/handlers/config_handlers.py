"""
.. py:module:: config_handler
   :synopsis: rest handler for config interaction.
"""
import logging,time
from twisted.internet import reactor, defer
from twisted.web.resource import Resource,NoResource
from twisted.web import resource, http
from twisted.python import log,failure
from twisted.python.log import PythonLoggingObserver
from twisted.web.server import NOT_DONE_YET
from twisted.internet.task import deferLater
from twisted.internet.error import ConnectionDone
from doboz_web.core.server.rest.handlers.default_rest_handler import DefaultRestHandler
from doboz_web.core.server.rest.request_parser import RequestParser
from doboz_web.core.server.rest.response_generator import ResponseGenerator
from doboz_web.core.components.updates.update_manager import UpdateManager
from doboz_web.core.components.updates.update_manager import UpdateManager
from doboz_web.core.signal_system import SignalHander
class ConfigHandler(DefaultRestHandler):
    isLeaf=False
    def __init__(self,rootUri="http://localhost"):
        DefaultRestHandler.__init__(self,rootUri)
        self.logger=log.PythonLoggingObserver("dobozweb.core.server.rest.configHandler")
        self.valid_contentTypes.append("application/pollapli.config+json")   

        subPath=self.rootUri+"/updates"
        self.putChild("updates",UpdatesHandler(subPath))
        subPath=self.rootUri+"/events"
        self.putChild("events",GlobalEventsHandler(subPath))
    def render_GET(self, request):
        """
        Handler for GET requests of config
        """
        
        def extract_args(result):
            return(self.environmentManager.get_environment(self.envId))            
        r=ResponseGenerator(request,status=200,contentType="application/pollapli.environment+json",resource="environment",rootUri=self.rootUri)
        d=RequestParser(request,"environment",self.valid_contentTypes,self.validGetParams).ValidateAndParseParams()
        d.addCallbacks(extract_args,errback=r._build_response)
        d.addBoth(r._build_response)    
        request._call=reactor.callLater(0,d.callback,None)
        return NOT_DONE_YET
  
    def render_PUT(self,request):
        """
        Handler for PUT requests of config
        """
        @defer.inlineCallbacks
        def extract_args(result):
            print("in extract args",result)
            name=result["name"] or ""
            description=result.get("description") or ""
            status=result.get("status") or "live"
            id=self.envId
            defer.returnValue((yield self.environmentManager.update_environment(id=id,name=name,description=description,status=status)))
        
        r=ResponseGenerator(request,status=200,contentType="application/pollapli.environment+json",resource="environment",rootUri=self.rootUri)
        d=RequestParser(request,"environment",self.valid_contentTypes,self.validGetParams).ValidateAndParseParams()    
        d.addCallbacks(extract_args,errback=r._build_response)    
        d.addBoth(r._build_response)
        request._call=reactor.callLater(0,d.callback,None)
        return NOT_DONE_YET
            
    def render_DELETE(self,request):
        """ 
        Handler for DELETE requests of environment
        WARNING !! needs to be used very carefully, with confirmation on the client side, as it deletes the
        current environment completely
        """
        r=ResponseGenerator(request,status=200,rootUri=self.rootUri)
        d=self.environmentManager.remove_environment(self.envId)
        d.addBoth(r._build_response)
        request._call=reactor.callLater(0,d.callback,None)
        return NOT_DONE_YET   


class UpdatesHandler(DefaultRestHandler):
    isLeaf=False
    def __init__(self,rootUri="http://localhost"):
        DefaultRestHandler.__init__(self,rootUri)
        self.valid_contentTypes.append("application/pollapli.updateList+json")  
        self.validGetParams.append('name')
        self.validGetParams.append('type')
        self.validGetParams.append('downloaded')
        self.validGetParams.append('installed') 

    def render_GET(self, request):
        """
        Handler for GET requests of updates
        """
     
        r=ResponseGenerator(request,status=200,contentType="application/pollapli.updateList+json",resource="updates",rootUri=self.rootUri)
        d=RequestParser(request,"updates",self.valid_contentTypes,self.validGetParams).ValidateAndParseParams()
        d.addCallbacks(UpdateManager.get_updates,errback=r._build_response)
        d.addBoth(r._build_response)
        request._call=reactor.callLater(0,d.callback,None)
        return NOT_DONE_YET
  
            
    def render_DELETE(self,request):
        """ 
        Handler for DELETE requests of addOns
        WARNING !! needs to be used very carefully, with confirmation on the client side, as it deletes
        all addons completely
        """
        r=ResponseGenerator(request,status=200)
        d=UpdateManager.clear_addOns()
        d.addBoth(r._build_response)
        request._call=reactor.callLater(0,d.callback,None)
        return NOT_DONE_YET   
    
class AddonsHandler(DefaultRestHandler):
    isLeaf=False
    def __init__(self,rootUri="http://localhost"):
        DefaultRestHandler.__init__(self,rootUri)
        self.logger=log.PythonLoggingObserver("dobozweb.core.server.rest.pluginsHandler")
        self.environmentManager=environmentManager
        self.envId=envId   
        self.valid_contentTypes.append("application/pollapli.addonList+json")   
        subPath=self.rootUri+"/"+str(self.envId)
        self.putChild("addons",NodesHandler(subPath,self.environmentManager,self.envId)  
)

    def render_GET(self, request):
        """
        Handler for GET requests of addOns
        """
        r=ResponseGenerator(request,status=200,contentType="application/pollapli.addonList+json",resource="addOns",rootUri=self.rootUri)
        d=RequestParser(request,"addOns",self.valid_contentTypes,self.validGetParams).ValidateAndParseParams()
        d.addCallbacks(UpdateManager.get_addOns,errback=r._build_response)
        d.addBoth(r._build_response)
        request._call=reactor.callLater(0,d.callback,None)
        return NOT_DONE_YET
  
            
    def render_DELETE(self,request):
        """     
        Handler for DELETE requests of addOns
        WARNING !! needs to be used very carefully, with confirmation on the client side, as it deletes
        all addons completely
        """
        r=ResponseGenerator(request,status=200,rootUri=self.rootUri)
        d=UpdateManager.clear_addOns()
        d.addBoth(r._build_response)
        request._call=reactor.callLater(0,d.callback,None)
        return NOT_DONE_YET   


class DispatchableEvent(object):
    EXPOSE=["signal","sender","senderInfo","data","time"]
    def __init__(self,signal=None,sender=None,data=None,realsender=None,time=None):
        self.signal=signal
        self.sender=sender
        self.data=data
        self.senderInfo=realsender
        self.time=time


class ClientHandler(object):
    def __init__(self):
        self.clients={}
        self.lastNotificationTime=time.time()
        self.notificationBuffer=[]
        
    def add_delegate(self,result,deffered,request):  
        print("in adding delegates")
        request.notifyFinish().addBoth(self.connectionCheck,request)  
        self.clients[request.clientId]=ClientDelegate(deffered,request)
        #print("ADDING DELEGATE: id:",request.clientId," total clients:",len(self.clients.keys()))
        print(" total clients:",len(self.clients.keys()))

        self.notify_all()
            
        

    def connectionCheck(self,result,request):    
        del self.clients[request.clientId] 
        print(" total clients:",len(self.clients.keys()))
        if isinstance(result,failure.Failure):
            error = result.trap(ConnectionDone)
            if error==ConnectionDone:
                pass
       
    def add_event(self,event):
        print("in adding event")
        self.notificationBuffer.append(event)
        self.notify_all()
        
    def _filterEvents(self,timestamp):
        data=[]
        for event in self.notificationBuffer:
            #print("EventTime",event.time*1000,"timestamp",int(timestamp))
            #print("is it bigger",long(event.time*1000)>timestamp)
            if long(event.time*1000)>timestamp:
                data.append(event)
        return data
            #[event for event in self.notificationBuffer if event.time>=timestamp ]
            #1313161679 ### 1313161675
            #1313161877.401
            #1313161886.0526619,
            #1313161959318.4709,
            #1313161957235
        
    def notify_all(self):
       # print("NOTIFICATION",len(self.clients.items()))
        for k,v in self.clients.items():
            if v:
                data=self._filterEvents(v.request.timestamp)
                if len(data)>0:
                    v.notify(self._filterEvents(v.request.timestamp))

     
       # print("NOTIFICATION Done",len(self.clients.items()))


class ClientDelegate(object):
    def __init__(self,deffered,r):
        self.deferred=deffered
        self.request = r

    def end(self, data):

        r=ResponseGenerator(self.request,status=200,contentType="application/pollapli.eventList+json",resource="events",rootUri="/rest/config/events")
        r._build_response(data)
        
    def notify(self, data):
        self.end( data)


class GlobalEventsHandler(DefaultRestHandler):
    
    isLeaf=True
    def __init__(self,rootUri="http://localhost"):
        DefaultRestHandler.__init__(self,rootUri)  
        self.valid_contentTypes.append("application/pollapli.eventList+json")   
        self.signalChannel="global_event_listener"
        self.signalHandler=SignalHander(self.signalChannel)
        self.signalHandler.add_handler(channel="driver_manager",handler=self._signal_Handler)   
        self.signalHandler.add_handler(channel="update_manager",handler=self._signal_Handler)
        self.signalHandler.add_handler(channel="environment_manager",handler=self._signal_Handler)
        self.signalHandler.add_handler(channel="node_manager",handler=self._signal_Handler)
        self.lastSignal=DispatchableEvent()
        
        self.clientHandler=ClientHandler()
        

    def _signal_Handler(self,signal=None,sender=None,realsender=None,data=None,time=None,*args,**kwargs):      
       # log.msg("In rest event handler ", " recieved ",signal," from ",sender, "with data" ,data," addtional ",args,kwargs,logLevel=logging.CRITICAL)
        self.clientHandler.add_event(DispatchableEvent(signal,sender,data,realsender,time))


          
    def render_GET(self, request):
        """
        Handler for GET requests of events
        """
        r=ResponseGenerator(request,status=200,contentType="application/pollapli.eventList+json",resource="events",rootUri=self.rootUri)
        d=RequestParser(request,"events",self.valid_contentTypes,self.validGetParams).ValidateAndParseParams()
        d.addCallbacks(self.clientHandler.add_delegate,callbackArgs=[d,request],errback=r._build_response)
        request._call=reactor.callLater(0,d.callback,None)
    
        return NOT_DONE_YET
  
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
        self.validGetParams.append('id')
        self.validGetParams.append('name')
        self.validGetParams.append('type')
        self.validGetParams.append('downloaded')
        self.validGetParams.append('installed') 
        
    def getChild(self, id, request):
        try:
            return UpdateHandler(self.rootUri+"/"+str(id),int(id))  
        except ValueError :
             return self#no id , so return self
         
    def render_GET(self, request):
        """
        Handler for GET requests of updates' list
        """
        r=ResponseGenerator(request,status=200,contentType="application/pollapli.updateList+json",resource="updates",rootUri=self.rootUri)
        d=RequestParser(request,"updates",self.valid_contentTypes,self.validGetParams).ValidateAndParseParams()
        d.addCallbacks(lambda params: UpdateManager.get_updates(params),errback=r._build_response)
        d.addBoth(r._build_response)
        request._call=reactor.callLater(0,d.callback,None)
        return NOT_DONE_YET
  


class UpdateHandler(DefaultRestHandler):
    isLeaf=False
    def __init__(self,rootUri="http://localhost",updateId=None):
        DefaultRestHandler.__init__(self,rootUri)
        self.updateId=updateId
        self.valid_contentTypes.append("application/pollapli.update+json")  
        self.validGetParams.append('id')
        self.validGetParams.append('name')
        self.validGetParams.append('type')
        self.validGetParams.append('downloaded')
        self.validGetParams.append('installed') 
        subPath=self.rootUri+"/status"
        self.putChild("status",UpdateStatusHandler(subPath,self.updateId)  
)
        
         
    def render_GET(self, request):
        """
        Handler for GET requests for a single update
        """
        r=ResponseGenerator(request,status=200,contentType="application/pollapli.update+json",resource="update",rootUri=self.rootUri)
        d=RequestParser(request,"update",self.valid_contentTypes,self.validGetParams).ValidateAndParseParams()
        d.addCallbacks(lambda params: UpdateManager.get_update(id=self.updateId),errback=r._build_response)
        d.addBoth(r._build_response)
        request._call=reactor.callLater(0,d.callback,None)
        return NOT_DONE_YET
    
class UpdateStatusHandler(DefaultRestHandler):
    isLeaf=True
    
    def __init__(self,rootUri="http://localhost",updateId=None):
        DefaultRestHandler.__init__(self,rootUri)
        self.updateId=updateId
        self.valid_contentTypes.append("application/pollapli.update.status+json")  
        self.validGetParams.append('id')
        self.validGetParams.append('name')
        self.validGetParams.append('type')
        self.validGetParams.append('downloaded')
        self.validGetParams.append('installed') 
      
    def render_POST(self,request):  
        """
        Handler for POST request for a specific update's status: this allows to start the download/setup process
        """ 
        
        def dostuff(result):
            if result["start"]:
                name=UpdateManager.get_update(id=self.updateId).name
                print("update to download",name)
                UpdateManager.downloadAndInstall_update(name)            
            else:
                print("uh oh")
        
        r=ResponseGenerator(request,status=200,contentType="application/pollapli.update.status+json",resource="update status",rootUri=self.rootUri)
        d=RequestParser(request,"update status",self.valid_contentTypes,self.validGetParams).ValidateAndParseParams()    
        d.addCallbacks(callback=dostuff,errback=r._build_response)    
        d.addBoth(r._build_response)
        request._call=reactor.callLater(0,d.callback,None)
        return NOT_DONE_YET

         
    def render_GET(self, request):
        """
        Handler for GET requests for a single update
        """
        r=ResponseGenerator(request,status=200,contentType="application/pollapli.update.Status+json",resource="update status",rootUri=self.rootUri)
        d=RequestParser(request,"update status",self.valid_contentTypes,self.validGetParams).ValidateAndParseParams()
        d.addCallbacks(lambda params: UpdateManager.get_update(id=self.updateId),errback=r._build_response)
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
    EXPOSE=["signal","sender","data","time"]
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
        print("in adding delegates: real time stamp",result["altTimeStamp"],"normal timestamp",request.timestamp)
        
        
        request.altTimeStamp=result["altTimeStamp"][0]
        if isinstance(request.altTimeStamp,str):
            request.altTimeStamp=float(request.altTimeStamp)
        
        request.notifyFinish().addBoth(self.connectionCheck,request)  
        self.clients[request.clientId]=ClientDelegate(deffered,request)
        #print("ADDING DELEGATE: id:",request.clientId," total clients:",len(self.clients.keys()))
        print(" total clients:",len(self.clients.keys()))
        self.notify_all()
            
        

    def connectionCheck(self,result,request):    
        del self.clients[request.clientId] 
        #print(" total clients:",len(self.clients.keys()))
        if isinstance(result,failure.Failure):
            error = result.trap(ConnectionDone)
            if error==ConnectionDone:
                pass
       
    def add_event(self,event):
        print("in adding event",event.signal)
        self.notificationBuffer.append(event)
        if len(self.notificationBuffer)>50:
            removed=self.notificationBuffer.pop(0)
            print("removed event",removed.signal)
        print("Total events",len(self.notificationBuffer))
       
        self.notify_all()
        
        
 
   
 
    def _filterEvents(self,timestamp):
        #print("filtering events with timestamp:",timestamp)
       
        data=[]
        for event in self.notificationBuffer:
            
            if isinstance(timestamp,long):
               
                eventTime=long(event.time*1000)
                #print("event",event.signal, "EventTime",eventTime,"timestamp",timestamp, "bigger?",eventTime>timestamp)
                if eventTime>timestamp:
                    data.append(event)
            else:
                
                eventTime=event.time
                
               # print("event",event.signal, "EventTime",eventTime,"timestamp",timestamp, "bigger?",eventTime>timestamp)
                if eventTime>timestamp:
                    data.append(event)
       
        return data
            #[event for event in self.notificationBuffer if event.time>=timestamp ]
           
        
    def notify_all(self):
        for k,v in self.clients.items():
            if v:
                data=self._filterEvents(v.request.altTimeStamp)
                if len(data)>0:
                    v.notify(data)



class ClientDelegate(object):
    def __init__(self,deffered,r):
        self.deferred=deffered
        self.request = r

    def end(self, data):
        print("Sending out to client",self.request.clientId ,"data",str(data))
        r=ResponseGenerator(self.request,status=200,contentType="application/pollapli.eventList+json",resource="events",rootUri="/rest/config/events")
        r._build_response(data)
        
    def notify(self, data):
        self.end( data)


class GlobalEventsHandler(DefaultRestHandler):
    
    isLeaf=True
    def __init__(self,rootUri="http://localhost"):
        DefaultRestHandler.__init__(self,rootUri)  
        self.valid_contentTypes.append("application/pollapli.eventList+json")   
        self.validGetParams.append('altTimeStamp')
        
        
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
  
function parseEvent(response,key)
{
    eventArgs=response.signal.split('.');
    eventType=eventArgs[eventArgs.length-1];
    eventData=response.data;
    
    targetElement=null;
    targetElementId=null;
    data=response.data;
    
    console.log("long poll event recieved "+eventType);
    
    if (eventType =="node_created")
    {
      targetElement=eventArgs[eventArgs.length-2];
      targetElementId=targetElement.split("_").pop();
      data={"name":response.data.name};
    }
    else if (eventType=="plugged_In")
    {
      targetElement=eventArgs[eventArgs.length-3];
      targetElementId=targetElement.split("_").pop();
    }
    else if (eventType=="plugged_Out")
    {
      targetElement=eventArgs[eventArgs.length-3];
      targetElementId=targetElement.split("_").pop();
    }
    else if (eventType=="download_updated")
    {
      targetElement=eventArgs[eventArgs.length-2]
      id=targetElement.split("_").pop()
      
      console.log("update_id of download "+id+ " data "+ JSON.stringify(eventData)+ " progress "+eventData.progress);
      //$("#mainmenu_lastNotification").text(targetElement+" "+_event);
      //pollapli.ui.set_progressbar("#progbardiv_"+id,eventData.progress*100);
    }
    return {time:response.time,signal:response.signal,sender:response.sender,data:data,"eventType":eventType,"targetElement":targetElement,"targetElementId":targetElementId};
}

var LongPollEvent = Backbone.Model.extend(
{
  //urlRoot : pollapli.mainUrl+'rest/config/updates',
  initialize: function()
  {  
  },
  defaults: 
  {
    
     time:(new Date()).getTime(),
     signal:"",
     sender:"",
     eventType:null,
     targetElementId:-1,
     targetElement:null
  },
  parse:function(response)
  {
    
    eventArgs=element.signal.split('.');
    eventType=eventArgs[eventArgs.length-1];
    eventData=element.data;

    console.log("long poll event recieved"+eventType);
    
    if (eventType =="node_created")
    {
      targetElement=eventArgs[eventArgs.length-2]
    }
    else if (eventType=="plugged_Out")
    {
      targetElement=eventArgs[eventArgs.length-3]
      targetElementId=targetElement.split("_").pop()
    }
    return {time:response.time,signal:response.signal,sender:response.sender,"eventType":eventType,"targetElement":targetElement,"targetElementId":targetElementId};
  }
});

var LongPollEvents = Backbone.Collection.extend(
{
  model : LongPollEvent,
  url: pollapli.mainUrl+'rest/config/events',
  
  initialize: function()
  {  
    this.timeOut= 2000;
    this.initialFetch=true;
    this.timeOutFunct=null;
    this.lastPollTime=(new Date()).getTime();  
    this.bind("add",this.updateTimeStamp );
  
    console.log("events init: lastPollTime:"+this.lastPollTime);
  },
  parse: function(response) 
  {
    console.log("long poll event recieved"+JSON.stringify(response.events.items)+"last event time"+this.lastPollTime); 
    return _.map(response.events.items, parseEvent);
  },
  updateTimeStamp:function()
  {
    console.log("Total events"+this.length)
    if (this.length>0)
    {
      this.lastPollTime=this.last().get("time");
     
      console.log("Parsing time from latest event: last event time"+this.lastPollTime);
      if (this.length>3)
      {
        this.remove(this.first(this.length-3));
      }
    }
    this.longPoll();
  },
  
  startLongPoll:function(response)
  {
    this.retry();
  },
  
  stopLongPoll:function()
  {
    if(this.timeOutFunct !=null)
    {
      this.timeOutFunct.cancel();
    }
  },
  
  longPoll:function()
  { 
    this.fetch( { data: { "altTimeStamp": this.lastPollTime, "clientId":pollapli.clientId },add: true });
  },
  retry:function()
  {
    
    self=this;
    setTimeout
    (
      function()
      {
        self.longPoll();
      },
      this.timeOut
      
    );
  }
 
});
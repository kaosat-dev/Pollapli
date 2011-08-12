function Manager(mainUrl,clientId)
{
  this.mainUrl=mainUrl;
  this.clientId=clientId;
  this.drivers;
  this.environments;
  this.errors=new Array();
  
/*$(document).ajaxError(function(e, xhr, settings, exception) { 
alert('error in: ' + settings.url + ' \n'+'error:\n' + xhr.responseText ); 
});*/ 
}

Manager.prototype.fetchData=function(dataUrl,contentType,successCallback,errorCallback,timeout)
    {
        
       /* if(!errorCallback)
          errorCallback=this.genericErrorHandler;
        
        if (!successCallback)
        successCallback=this.genericSuccessHandler;
        
        if (!contentType)
          contentType="application/pollapli.eventList+json"*/
        if(!timeout)
          timeout=500000;
          
            response=$.ajax({
                    url: dataUrl+"?clientId="+this.clientId+"&_"=+new Date(),
                    method: 'GET',
                    async: true,
                    cache:false,
                    dataType: 'jsonp',
                    timeout:timeout,
                    contentType: contentType,
                    success: successCallback,
                    error:errorCallback,
                    complete: this.genericCompleteHandler,
                    cache:false
                });

    }



Manager.prototype.genericCompleteHandler=function (response)
    {
        console.log("Ajax complete "+response)    ; 
    }

    
Manager.prototype.genericSuccessHandler=function (response)
    {
        console.log("Ajax sucess "+response)    ; 
    }
Manager.prototype.genericErrorHandler=function (response, strError)
    { 
      errorInfo=$.parseJSON(response.responseText);
      console.log("Error: "+errorInfo.errorCode+" msg: "+errorInfo.errorMessage+" raw: "+strError)
      $('#errors').jqoteapp('#errors_tmpl', errorInfo);
        
       // this.errors.push(response);
       // alert("jqXHR"+request+" textStatus"+textStatus+" errorThrown"+errorThrown);
        
    } 
    
////////////////////////////////////////////////////////////////
//Initial retrieval of data
Manager.prototype.init=function ()
{
  this.initRequesters()

}

Manager.prototype.initRequesters=function ()
{
  var self = this; 
  setTimeout
  (
    function()
    {
      manager.fetchEnvironments(manager);
      manager.longPoll(manager);
    },
/*    ("manager.fetchEnvironments(manager)",
     "manager.longPoll(manager)"),*/
    1000
  );
  
}

Manager.prototype.longPoll=function (self)
{
  self.fetchData(self.mainUrl+"rest/config/events",'application/pollapli.eventList+json',
  function (response)
  {   
   
    $('#events').jqoteapp('#events_tmpl', response.events.items);
    self.longPoll(self);
    },
  function (response)
  {
    
     // self.genericErrorHandler(response)
      self.longPoll(self);
  }
); 
}

Manager.prototype.fetchEnvironments=function (self)
{

  self.fetchData(self.mainUrl+"rest/environments/",'application/pollapli.envirodnmentList+json',
  function (response)
  {
    self.environments=response;
   },
   
  self.genericErrorHandler); 
}









Manager.prototype.test=function ()
{
  var self = this; 

  this.fetchData(this.mainUrl+"rest/environments",'application/pollapli.environmentList+json',function (response){self.genericSuccessHandler(response)},function (response){self.genericErrorHandler(response)}); 
}


Manager.prototype.test2=function ()
{
  var self = this; 
  var descFld="Description"
  var nameFld="Name"
  var status="status"
  this.fetchData(this.mainUrl+"rest/environments",'application/pollapli.environmentList+json',
  function (response){
    $('#environments').jqoteapp('#environments_tmpl', response.environments.items);
    $('#environmentsheader').jqotesub('#header_tmpl',{ nameFld:"Name", descFld:"Description" });
    },
  function (response){self.genericErrorHandler(response)}); 
}

Manager.prototype.test3=function ()
{
  var self = this; 
  var descFld="Description"
  var nameFld="Name"
  this.fetchData(this.mainUrl+"rest/environments/1/nodes",'application/pollapli.nodeList+json',
  function (response)
  {
    $('#nodes').jqotesub('#nodes_tmpl', response.nodes.items);
    $('#header').jqotesub('#header_tmpl',{ nameFld:"Name", descFld:"Description" });
   }
    ,function (response){self.genericErrorHandler(response)}); 
}

Manager.prototype.test4=function ()
{
  var self = this; 
  var descFld="Description"
  var nameFld="Name"
  this.fetchData(this.mainUrl+"rest/config/updates",'application/pollapli.updateList+json',
  function (response)
  {
    $('#updates2').jqoteapp('#updates2_tmpl', response.updates.items);
    thingy();
   // $('#bla').jScrollPane({autoReinitialise: false, showArrows:true ,horizontalGutter: 10});
  
   }
    ,function (response){self.genericErrorHandler(response)}); 
}




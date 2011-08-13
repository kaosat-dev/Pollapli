var pollapli = pollapli = pollapli || {}




////////helpers
function S4() {
   return (((1+Math.random())*0x10000)|0).toString(16).substring(1);
}
function guid() {
   return (S4()+S4()+"-"+S4()+"-"+S4()+"-"+S4()+"-"+S4()+S4()+S4());
}



pollapli.mainUrl="http://"+window.location.host+"/";
pollapli.clientId=guid();



pollapli.Manager=function Manager()
{
  this.mainUrl=pollapli.mainUrl;
  this.clientId=pollapli.clientId;
  this.drivers;
  this.environments=new Array();
  this.updates=new Array();
  this.errors=new Array();
  this.tutu="tutu";
  
/*$(document).ajaxError(function(e, xhr, settings, exception) { 
alert('error in: ' + settings.url + ' \n'+'error:\n' + xhr.responseText ); 
});*/ 
//alert(JSON.stringify(manager.environments[0]));
}

pollapli.Manager.prototype.fetchData=function(dataUrl,contentType,successCallback,errorCallback,timeout,method,data)
    {
        if(!method)
          method='GET';
          
         if(!data)
          data='';
         
          
        if(!errorCallback)
          errorCallback=this.genericErrorHandler;
        
        if (!successCallback)
        successCallback=this.genericSuccessHandler;
        
        if (!contentType)
          contentType="application/pollapli.eventList+json";
          
       if(!timeout)
          timeout=500000;
          
            $.ajax({
                    url: dataUrl+"?clientId="+this.clientId,
                    method: method,
                    async: true,
                    cache:false,
                    dataType: 'jsonp',
                    data:data,
                    contentType: contentType,
                    success: successCallback,
                    error:errorCallback,
                    complete: this.genericCompleteHandler,
                    cache:false
                });

    }


pollapli.Manager.prototype.postData=function(dataUrl,contentType,data)
    {
       
         if(!data)
          data='';
          
        
      

        $.ajax({
        type: 'POST',
        url: dataUrl+"?clientId="+this.clientId,
        data: data,
        contentType: contentType,
        success: this.genericSuccessHandler,
        dataType: 'jsonp',
      });


          /*  $.ajax({
                    url: dataUrl+"?clientId="+this.clientId,
                    method: 'POST',
                    async: true,
                    cache:false,
                    dataType: 'jsonp',
                    data:data,
                    contentType: contentType,
                    success: this.genericSuccessHandler,
                    error:this.genericErrorHandler,
                    complete: this.genericCompleteHandler,
                    cache:false
                });*/

    }



pollapli.Manager.prototype.genericCompleteHandler=function (response)
    {
        //console.log("Ajax complete "+response)    ; 
    }

    
pollapli.Manager.prototype.genericSuccessHandler=function (response)
    {
        console.log("Ajax sucess "+response)    ; 
    }
pollapli.Manager.prototype.genericErrorHandler=function (response, strError)
    { 
      errorInfo=$.parseJSON(response.responseText);
      console.log("Error: "+errorInfo.errorCode+" msg: "+errorInfo.errorMessage+" raw: "+strError)
      $('#errors').jqoteapp('#errors_tmpl', errorInfo);
        
       // this.errors.push(response);
       // alert("jqXHR"+request+" textStatus"+textStatus+" errorThrown"+errorThrown);
        
    } 
    
////////////////////////////////////////////////////////////////
//Initial retrieval of data
pollapli.Manager.prototype.init=function ()
{
  this.initRequesters()

}

pollapli.Manager.prototype.initRequesters=function ()
{
  var self = this; 
  setTimeout
  (
    function()
    {
      manager.fetchEnvironments(manager);
      manager.fetchNodes(manager,1);
      manager.fetchUpdates()
      manager.longPoll(manager);
      
    },
    1000
  );
  
}

pollapli.Manager.prototype.longPoll=function (self)
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
     setTimeout
    (
      function()
      {
        self.longPoll(self);
        
      },
      20000
    );
     
      
  }
); 
}

pollapli.Manager.prototype.fetchEnvironments=function (self)
{

  self.fetchData(self.mainUrl+"rest/environments/",'application/pollapli.environmentList+json',
  function (response)
  {
    
    
     //self.environments=response.environments.items;
     self.environments= self.environments.concat(response.environments.items);
      
    
   }); 
}

pollapli.Manager.prototype.fetchNodes=function (self,environmentId)
{

  self.fetchData(self.mainUrl+"rest/environments/"+environmentId+"/nodes",'application/pollapli.nodeList+json',
  function (response)
  {

     self.environments[environmentId-1].nodes=response.nodes.items;
     self.dostuff();
   }); 
}


pollapli.Manager.prototype.fetchNodes2=function (environmentId)
{

  manager.fetchData(manager.mainUrl+"rest/environments/"+environmentId+"/nodes",'application/pollapli.nodeList+json',
  function (response)
  {
    //$('#nodes').jqoteapp('#nodes_tmpl', response.nodes.items);
    manager.environments[environmentId-1].nodes=response.nodes.items;
   }); 
}

pollapli.Manager.prototype.fetchDriver=function (environmentId,nodeId)
{

  manager.fetchData(manager.mainUrl+"rest/environments/"+environmentId+"/nodes",'application/pollapli.nodeList+json',
  function (response)
  {

    $('#nodes').jqoteapp('#nodes_tmpl', response.nodes.items);
    
   }); 
}

pollapli.Manager.prototype.fetchUpdates=function ()
{

  manager.fetchData(manager.mainUrl+"rest/config/updates",'application/pollapli.updateList+json',
  function (response)
  {
    manager.updates=response.updates.items;
   }); 
}


pollapli.Manager.prototype.dostuff=function()
{
   $('#environments').jqotesub('#environments_tmpl', this.environments[0]);
   $('#nodes').jqotesub('#nodes_tmpl', this.environments[0].nodes);
}

pollapli.Manager.prototype.dostuff2=function()
{

   $('#updates').jqotesub('#updates_tmpl', this.updates);
   
   $("button").button();
     $( ".progressbar" ).progressbar({
      value: 37
    });   
   
  $(".progresswraper").show("fast");
    
    
    $(".progressbar > div").css({ 'background': 'Orange' });
    $(".progressbar ").css({ 'border-radius': 0+'px' });
    $(".progressbar > div").css({ 'border-radius': 0+'px'});
    
}

pollapli.Manager.prototype.postUpdateDownload=function()
{
  //this.fetchData({"dataUrl":manager.mainUrl+"rest/config/updates","contentType":'application/pollapli.updateList+json',"method":'POST'} );
  data='{"name":"reprap1","type":"reprap","description":"just a reprap node"}';
  resp=function (response)
  {
    alert("response ok"); 
  };
  
  url=manager.mainUrl+"rest/environments/1/nodes";
 // this.fetchData({"dataUrl":url,"contentType":'application/pollapli.nodeList+json',"method":'POST',"data":data} );
  
  
  this.postData(url,'application/pollapli.nodeList+json',data);
  //dataUrl,contentType,successCallback,errorCallback,timeout,method)
}

      





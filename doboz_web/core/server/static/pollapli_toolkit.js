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
  this.environments={ };
  this.updates=new Array();
  this.errors=new Array();
  
  
  this.tutu={};
  
  this.nodes=new Array();
  this.testEnvironment={ };
  
$(document).ajaxError(function(e, xhr, settings, exception) 
{ 
  
  //alert('error in: ' + settings.url + ' \n'+'error:\n' + xhr.responseText + "Exception"+exception); 
});
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


pollapli.Manager.prototype.postData=function(dataUrl,contentType,data,successCallback)
    {  
         if(!data)
          data='';
         if (!successCallback)
        {
          successCallback=this.genericSuccessHandler;
        }
        $.ajax({
        type: 'POST',
        async:true,
        cache:false,
        dataType: 'jsonp',
        url: dataUrl+"?clientId="+this.clientId,
        data: data,
        contentType: contentType,
        success: successCallback,
        error:this.genericErrorHandler
      });
    }
    
pollapli.Manager.prototype.putData=function(dataUrl,contentType,data,successCallback)
    {  
         if(!data)
          data='';


        if (!successCallback)
        {
          successCallback=this.genericSuccessHandler;
        }

        $.ajax({
        type: 'PUT',
        async:true,
        cache:false,
        dataType: 'jsonp',
        url: dataUrl+"?clientId="+this.clientId,
        data: data,
        contentType: contentType,
        success: successCallback,
        error:this.genericErrorHandler
      });

    }
    
pollapli.Manager.prototype.deleteData=function(dataUrl,contentType,data,successCallback)
{  
        if(!data)
        {
          data='';
        }
        if (!successCallback)
        {
          successCallback=this.genericSuccessHandler;
        }

        $.ajax({
        type: 'DELETE',
        async:true,
        cache:false,
        dataType: 'jsonp',
        url: dataUrl+"?clientId="+this.clientId,
        data: data,
        contentType: contentType,
        success: successCallback,
        error:this.genericErrorHandler
        
      });

}



pollapli.Manager.prototype.genericCompleteHandler=function (response)
    {
        console.log("Ajax complete "+response)    ; 
    }

    
pollapli.Manager.prototype.genericSuccessHandler=function (response)
    {
    
        console.log("Ajax sucess "+response)    ; 
    }
pollapli.Manager.prototype.genericErrorHandler=function (response, strError)
    { console.log("Error "+strError);
      
      //errorInfo=$.parseJSON(response.responseText);
      //console.log("Error: "+errorInfo.errorCode+" msg: "+errorInfo.errorMessage+" raw: "+strError)
      //$('#errors').jqoteapp('#errors_tmpl', errorInfo);
        
       // this.errors.push(response);
       // alert("jqXHR"+request+" textStatus"+textStatus+" errorThrown"+errorThrown);
        
    } 
    
////////////////////////////////////////////////////////////////
//Initial retrieval of data
pollapli.Manager.prototype.init=function ()
{
  this.initRequesters()

  //this.tutu[1]={};
 //  $("#bindingTest").link(this.environments[1],{name:"name",description:"toto"});
 //  $("#bindingTest").link(self.environments,{name:"name",description:"toto"});
 // $("#bindingTest input:text[id=toto]").val("NewValue");
 // alert($("#bindingTest input:text[id=name]").val());

}

pollapli.Manager.prototype.initRequesters=function ()
{
  var self = this; 
  setTimeout
  (
    function()
    {
      manager.fetchEnvironments(manager);
      
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


pollapli.Manager.prototype._setFields=function (sourceObject,resultObject)
{
   if(!resultObject)
   {
    resultObject={}; 
   }
   
   $.each(sourceObject,  function(key, value)
   {
      $(resultObject).setField(key, value); 
   });
   return resultObject;
}

pollapli.Manager.prototype.fetchEnvironments=function (self)
{
  self.fetchData(self.mainUrl+"rest/environments/",'application/pollapli.environmentList+json',
  function (response)
  {

     var add_environment=function (key,environment) 
     {

       finalEnv={};
       $("#bindingTest").link(finalEnv,{name:"name",description:"toto"});
       finalEnv=self._setFields(environment,finalEnv);
       $(self.environments).setField(environment.id+'',finalEnv);
      
     }
     $.each(response.environments.items,add_environment ); 
     
    
     manager.fetchNodes(manager,1);
 
   }); 
}

pollapli.Manager.prototype.fetchNodes=function (self,environmentId)
{

  self.fetchData(self.mainUrl+"rest/environments/"+environmentId+"/nodes",'application/pollapli.nodeList+json',
  function (response)
  {

     self.environments[environmentId].nodes=response.nodes.items;
     self.dostuff();
    // alert(JSON.stringify(manager.environments[1].nodes[0]));
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
   $('#environments').jqotesub('#environments_tmpl', this.environments[1]);
   $('#nodes').jqotesub('#nodes_tmpl', this.environments[1].nodes);
   $("button").button();
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



pollapli.Manager.prototype.create_node=function(data)
{
  url=manager.mainUrl+"rest/environments/1/nodes";
  this.postData(url,'application/pollapli.nodeList+json',JSON.stringify(data));
}

pollapli.Manager.prototype.update_node=function(data,nodeId)
{
  //data='{"name":"reprap1","type":"reprap","description":"just a reprap node"}';
  url=manager.mainUrl+"rest/environments/1/nodes/"+nodeId;
  this.putData(url,'application/pollapli.node+json',JSON.stringify(data));
}

pollapli.Manager.prototype.deleteNode=function(nodeId)
{
  this.deleteData(manager.mainUrl+"rest/environments/1/nodes/"+nodeId,'application/pollapli.node+json',"",
  function(response)
  {
      alert("element deletion sucessfull");
  });
 // $(id).remove();
}



pollapli.Manager.prototype.fetchNodes2=function (environmentId)
{
  
  manager.fetchData(manager.mainUrl+"rest/environments/"+environmentId+"/nodes",'application/pollapli.nodeList+json',
  function (response)
  {
    var add_node=function (key,node) 
     {
       res={};
       res=manager._setFields(node,res);
       $(manager.nodes).setField(node.id+'',res);
      
     }
     $.each(response.nodes.items,add_node ); 
     $.each(manager.nodes,function(key,value){$('#nodes_test').jqoteapp('#nodes_test_tmpl',value)} ) ;  
    
   }); 
}


///////////////////////
//for testing

pollapli.Manager.prototype.getEnv2=function()
{
  manager.fetchData(manager.mainUrl+"rest/environments/1",'application/pollapli.environment+json',
  function(response)
  {
      //manager.testEnvironment=response.environment; 
     //for testing
     //$(manager.testEnvironment).link($("#environments_thingy"));//.trigger("change");;
     //$("#environments_thingy").link(manager.testEnvironment);
    
   // $(manager.testEnvironment).trigger("change");
   // $("#environments_thingy").trigger("changeField");
    
   $('#testDiv').jqotesub('#envs_tmpl',manager.testEnvironment);  
   //$("#tutu0").link(manager.testEnvironment); 
    $(manager.testEnvironment).setField("name",response.environment.name);
    $(manager.testEnvironment).setField("description",response.environment.description);
   
   //manager.tutu= $.jqotec('#envs_tmpl').toString()
   //alert(manager.tutu);   
   //alert(manager.testEnvironment.name);
   
   
    //alert(JSON.stringify(response));
    
  /*  $(source).link(target).trigger("change");
      alert(target.input1); // value

    // or in reverse
    $(source).link(target);
    $(target).trigger("changeField");

    alert($("[name=age]").val()); // target.age
    */
  });
}

pollapli.Manager.prototype.getNodesTest=function()
{
  manager.fetchData(manager.mainUrl+"rest/environments/"+1+"/nodes",'application/pollapli.nodeList+json',
  function (response)
  { 
    var tmpNodeList=new Array();
    var add_node=function (key,node) 
     {
       res={};
       res=manager._setFields(node,res);
       tmpNodeList.push(node);
     }
    
      $.each(response.nodes.items,add_node ); 
      //alert("tmpNodelist"+JSON.stringify(tmpNodeList));
      $(manager).setField("nodes",tmpNodeList); 
      manager.renderNodes();
   }); 
}

pollapli.Manager.prototype.deleteNodeTest=function(nodeId)
{
  this.deleteData(manager.mainUrl+"rest/environments/1/nodes/"+nodeId,'application/pollapli.node+json',"",
  function(response)
  {
      for(var i = manager.nodes.length-1; i >= 0; i--)
      { 
         if (nodeId==manager.nodes[i].id)
       {
         manager.nodes.splice(i,1);
         break;
       } 
      }
      $(manager).setField("nodes",manager.nodes); 
      manager.renderNodes();
  });
}



pollapli.Manager.prototype.addNodeTest=function(data)
{
  if (!data)
  {
    data={"name":"test","type":"test","description":"just a test"};
    data=JSON.stringify(data);
  }
  //alert("data"+data);
  this.postData(manager.mainUrl+"rest/environments/1/nodes/",'application/pollapli.nodeList+json',data,
  function(response)
  {
      manager.nodes.push(response.node);
      $(manager).setField("nodes",manager.nodes); 
      manager.renderNodes();
  });
}

pollapli.Manager.prototype.deleteNodes=function()
{
  self=this;
  this.deleteData(manager.mainUrl+"rest/environments/1/nodes/",'application/pollapli.nodeList+json',"",
  function(response)
  {
     // alert("self"+self+JSON.stringify(self));
      manager.nodes=[];
      $(manager).setField("nodes",manager.nodes); 
      manager.renderNodes();
  });
}

pollapli.Manager.prototype.updateNodeTest=function(data,nodeId)
{
 // 
  url=manager.mainUrl+"rest/environments/1/nodes/"+nodeId;
  this.putData(url,'application/pollapli.node+json',JSON.stringify(data),
  function(response)
  {
    
      node=manager.findNode(nodeId);
      if (node!=null)
      {
         node.name=data.name;
         node.description=data.description;
      }
      
      for(var i = manager.nodes.length-1; i >= 0; i--)
      { 
       if (nodeId==manager.nodes[i].id)
       {
         manager.nodes[i]=node;
         break;
       } 
      }
    
      $(manager).setField("nodes",manager.nodes); 
      manager.renderNodes();

  });
}

pollapli.Manager.prototype.findNode=function(id)
{
  for(var i = manager.nodes.length-1; i >= 0; i--)
      { 
       if (id==manager.nodes[i].id)
       {
         return manager.nodes[i];

       } 
      }
     return null;
}

pollapli.Manager.prototype.updateANode=function(id,newData)
{
  
}

pollapli.Manager.prototype.renderNodes=function()
{
   $('#testDiv_nodes').jqotesub('#nodes_tmpl',manager.nodes);   
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

      





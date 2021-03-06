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
  
  
  this.lastEvent=null;
  this.lastLongPollTimeStamp=(new Date()).getTime();
  this.nodes=new Array();
  this.testEnvironment={ };
  this.driverTypes=Array();
  this.files={}
  
$(document).ajaxError(function(e, xhr, settings, exception) 
{ 
  
  //alert('error in: ' + settings.url + ' \n'+'error:\n' + xhr.responseText + "Exception"+exception); 
});
//alert(JSON.stringify(manager.environments[0]));
}

pollapli.Manager.prototype.fetchData=function(dataUrl,contentType,successCallback,errorCallback,timeout,method,data,params)
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
                    url: dataUrl+"?clientId="+this.clientId+"&"+params,
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
    { 
      console.log("Error "+strError);
      
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
      self.fetchFiles();
      self.getNodesTest();
      self.getDriverTypes();
      manager.longPoll(manager);
      
    },
    500
  );
  
}

pollapli.Manager.prototype.longPoll=function (self)
{
  //curTimeStamp=(new Date()).getTime();

  self.fetchData(self.mainUrl+"rest/config/events",'application/pollapli.eventList+json',
  function (response)
  {   
    self.handleNodeEvent(response.events.items);
    $('#events').jqoteapp(pollapli.ui.templates.events_tmpl, response.events.items);
    var nEvent=response.events.items.pop();
    if(nEvent)
    {
      self.lastEvent=nEvent;
      self.lastLongPollTimeStamp=self.lastEvent.time;
    }
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

  },null,null,"altTimeStamp="+self.lastLongPollTimeStamp
); 
}

pollapli.Manager.prototype.fetchFiles=function ()
{
  self=this;
  this.fetchData(self.mainUrl+"rest/config/files",'application/pollapli.fileList+json',
  function (response)
  {
     self.files=response.files.items;
   }); 
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

    $('#nodes').jqoteapp(pollapli.ui.templates.nodes_old_tmpl, response.nodes.items);
    
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
   $('#environments').jqotesub(pollapli.ui.templates.environments_tmpl, this.environments[1]);
   $('#nodes').jqotesub(pollapli.ui.templates.nodes_old_tmpl, this.environments[1].nodes);
   $("button").button();
}

pollapli.Manager.prototype.dostuff2=function()
{

   $('#updates').jqotesub(pollapli.ui.templates.updates_tmpl, this.updates);
   
   $("button").button();
   
   pollapli.ui.init_progressbar(".progressbar",15);


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
     $.each(manager.nodes,function(key,value){$('#nodes_test').jqoteapp(pollapli.ui.templates.nodes_test_tmpl,value)} ) ;  
    
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
    
   $('#testDiv').jqotesub(pollapli.ui.templates.envs_tmpl,manager.testEnvironment);  
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
  
      $("#loader_dialog").dialog('close');
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
  
  self=this;
  if (!data)
  {
    data={"name":"test","type":"test","description":"just a test"};
   
  }
   data=JSON.stringify(data);
  //alert("data"+data);
  this.postData(manager.mainUrl+"rest/environments/1/nodes/",'application/pollapli.nodeList+json',data,
  function(response)
  {
    
      self.addANode(response.node);
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

pollapli.Manager.prototype.addANode=function(node)
{
  if( manager.findNode (node.id)==null)
      {
       manager.nodes.push(node);
     
      }
  
  
}

pollapli.Manager.prototype.removeANode=function(nodeId)
{
  for(var i = manager.nodes.length-1; i >= 0; i--)
      { 
         if (nodeId==manager.nodes[i].id)
       {
         manager.nodes.splice(i,1);
         break;
       } 
      }
}

pollapli.Manager.prototype.updateANode=function(newNode)
{
  for(var i = manager.nodes.length-1; i >= 0; i--)
      { 
         if (newNode.id==manager.nodes[i].id)
       {
         manager.nodes.splice(i,1,newNode);
         break;
       } 
      }
}

pollapli.Manager.prototype.handleNodeEvent=function(nodeEvents)
{

  var analyse=function(key,element)
  {
    eventArgs=element.signal.split('.');
    _event=eventArgs[eventArgs.length-1];
    
    eventData=element.data;
  
     $("#mainmenu_lastNotification").text(_event);
    
    console.log("event recieved"+_event);
    
    if (_event =="node_created")
    {
      targetElement=eventArgs[eventArgs.length-2]
      //alert("event: "+_event+" element created: "+targetElement);
    }
    else if (_event=="node_deleted")
    {
      targetElement=eventArgs[eventArgs.length-2]
      //alert("event: "+_event+" element deleted: "+targetElement);
    }
    else if (_event=="plugged_Out")
    {
      targetElement=eventArgs[eventArgs.length-3]
      id=targetElement.split("_").pop()
      $("#mainmenu_lastNotification").text(targetElement+" "+_event);
      //alert("event: "+_event+" element plugged Out: "+targetElement+ " with id: "+id);
    }
      else if (_event=="plugged_In")
    {
      targetElement=eventArgs[eventArgs.length-3]
      id=targetElement.split("_").pop()
      $("#mainmenu_lastNotification").text(targetElement+" "+_event);
      //alert("event: "+_event+" element plugged Out: "+targetElement+ " with id: "+id);
    }
    if (_event=="download_updated")
    {
      targetElement=eventArgs[eventArgs.length-2]
      id=targetElement.split("_").pop()
      $("#mainmenu_lastNotification").text(targetElement+" "+_event);
      console.log("update_id of download "+id+ " data "+ JSON.stringify(eventData)+ " progress "+eventData.progress);
      
      pollapli.ui.set_progressbar("#progbardiv_"+id,eventData.progress*100);
    }
    
    
    if(_event=="node_created")
    {
      manager.addANode(element.data);
      manager.renderNodes();    
    }
    else if(_event=="node_updated")
    {
        manager.updateANode(element.data);
        manager.renderNodes(); 
    }
    else if(_event=="node_deleted")
    {
      manager.removeANode(element.data.id);
      manager.renderNodes();
    }
    else if(_event=="nodes_cleared")
    {
      manager.nodes=[]
      manager.renderNodes();
    }
  }
  
  $.each(nodeEvents,analyse ); 
   
}



pollapli.Manager.prototype.renderNodes=function()
{
  
  try
  {
    $('#testDiv_nodes').jqotesub(pollapli.ui.templates.nodes_tmpl,manager.nodes); 
    //$('#testDiv_nodes button').button();  
  }
catch(err)
  {
  alert("erroooor"+err)
  }
   
}

pollapli.Manager.prototype.dumpNodes=function()
{
  alert("Nodes"+JSON.stringify(this.nodes));
}


pollapli.Manager.prototype.getDriverTypes=function()
{
  var self=this;
  manager.fetchData(this.mainUrl+"rest/drivertypes/",'application/pollapli.driverTypeList+json',
  function (response)
  { 
    self.driverTypes=response.driverTypes.items;
   }); 
}


pollapli.Manager.prototype.start_UpdateDownloadInstall=function(updateId)
{
  var data={"start":true}
  data=JSON.stringify(data);
  this.postData(manager.mainUrl+"rest/config/updates/"+updateId+"/status",'application/pollapli.update.status+json',data,
  function(response)
  {
   

     // manager.renderNodes();
  });
  
}
/*
pollapli.validateExtension=function(filePath)
{
  var ext = filePath.substring(filePath.lastIndexOf('.') + 1).toLowerCase();
  if(ext!="gcode")
  {
    return false;
  }
  return true;
}

pollapli.uploadFile()
{
  if(this.validateExtension($("input[name=datafile]").val()))
   {
   $("#uploadProgress").show();
   var self = this; 
   this.uploadTimer=setInterval(function()
   { 
      self.getUploadProgress(); 
   }, 500); 
   }
   else
   {
     alert("not a good file format");
   }
  
}
     */ 
     
 
pollapli.Manager.prototype.removeFiles=function(fileName)
{
  this.files=[];
} 
     
pollapli.Manager.prototype.removeAFile=function(fileName)
{
  
  for(var i = this.files.length-1; i >= 0; i--)
      { 
         if (fileName==this.files[i].name)
       {
         this.files.splice(i,1);
         break;
       } 
      }
}
pollapli.Manager.prototype.deleteFile=function(fileName)
{
  self=this;
  this.deleteData(
    manager.mainUrl+"rest/config/files/"+fileName,'application/pollapli.file+json',"{}",
  function(response)
  {
    
    self.removeAFile(fileName)
    pollapli.ui.render_filesList();

  }
  );
}

pollapli.Manager.prototype.deleteFiles=function()
{
  self=this;
  this.deleteData(
    manager.mainUrl+"rest/config/files",'application/pollapli.fileList+json',"{}",
  function(response)
  {
    
    self.removeFiles()
    pollapli.ui.render_filesList();

  }
  );
}




<script type="text/x-jqote-template" id="events_tmpl"> 
    <div>
    <% 
      var dt=new Date((Number(this.time))*1000);    
      var convTime=(dt.getMonth()+1)+ '/'+dt.getDate()+ '/'+dt.getFullYear() +" "+ dt.getHours() + ':' + dt.getMinutes() + ':' + dt.getSeconds() ;
      
      var currentTime=(new Date()).getTime();
      dt=new Date();     
      currentTime=(dt.getMonth()+1)+ '/'+dt.getDate()+ '/'+dt.getFullYear() +" "+ dt.getHours() + ':' + dt.getMinutes() + ':' + dt.getSeconds() ;
      
      try
      {
      var lastEventTime=manager.lastEvent.time;
      dt=new Date((Number(lastEventTime))*1000);     
      lastEventTime=(dt.getMonth()+1)+ '/'+dt.getDate()+ '/'+dt.getFullYear() +" "+ dt.getHours() + ':' + dt.getMinutes() + ':' + dt.getSeconds() ;
      }
      catch(err)
      {
        var lastEventTime=0;
      }
      
      var data=JSON.stringify(this.data);
    %>
    <Strong>Signal: </Strong> <%= this.signal %>  <Strong>Sender: </Strong><%= this.sender %> <Strong>Data: </Strong> <%= data %>
     <strong> SenderInfo:</strong><%= this.senderInfo %><strong>Event Time:</strong><%= convTime %> <strong>Current Time:</strong><%= currentTime %>
      <strong>Last event Time:</strong><%= lastEventTime %>
     
     </div>
</script> 


<script type="text/x-jqote-template" id="errors_tmpl"> 
    <![CDATA[
    <div>
  
    <Strong>Error: Code: </Strong> <%= this.errorCode %>  <Strong>Message: </Strong><%= this.errorMessage %> 
     
     </div>
    ]]>
</script> 
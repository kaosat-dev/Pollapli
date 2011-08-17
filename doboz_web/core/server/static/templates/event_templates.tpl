<script type="text/x-jqote-template" id="events_tmpl"> 
    <div>
    <% 
      var dt=new Date((Number(this.time))*1000);
      this.time=(dt.getMonth()+1)+ '/'+dt.getDate()+ '/'+dt.getFullYear() +" "+ dt.getHours() + ':' + dt.getMinutes() + ':' + dt.getSeconds() ;
      var data=JSON.stringify(this.data);
    %>
    <Strong>Signal: </Strong> <%= this.signal %>  <Strong>Sender: </Strong><%= this.sender %> <Strong>Data: </Strong> <%= data %> <strong> SenderInfo:</strong><%= this.senderInfo %><strong>Time:</strong><%= this.time %>
     
     </div>
</script> 


<script type="text/x-jqote-template" id="errors_tmpl"> 
    <![CDATA[
    <div>
  
    <Strong>Error: Code: </Strong> <%= this.errorCode %>  <Strong>Message: </Strong><%= this.errorMessage %> 
     
     </div>
    ]]>
</script> 
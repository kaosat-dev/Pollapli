

<script type="text/x-jqote-template" id="nodes_tmpl"> 
    <% var divId="nodediv_"+j+'' ; %>
    <div id="<%=divId%>" class="ui-corner-all ui-state-default block">
      <div name="id" id="id">Id: <%=this.id%></div>
      <div name="name" id="name">Name: <%=this.name%></div>
      <div name="description" id="description">description: <%=this.description%></div>
      
      <% if(this.driver) { %>
            <div >isPluggedIn: <%=this.driver.isPluggedIn%></div>
            <div >isConnected: <%=this.driver.isConnected%></div>
            <button onclick="pollapli.ui.openDriverDialog(<%=j%>,'modify')">Modify driver </button>
        
      <% }else { %>
         <button onclick="pollapli.ui.openDriverDialog(<%=j%>,'set')">Set driver</button>
       <% }%>
      <br>
      <button onCLick=manager.deleteNodeTest(<%=this.id%>)>Delete</button>
      <button onClick=pollapli.ui.openNodeDialog_test(<%=j%>,"modify") > Update</button>
    </div>
</script> 


<script type="text/x-jqote-template" id="nodes_dialog_tmpl"> 
    <% if (!this.node)
    {
      this.node={name:"...",description:"...",type:"...",id:-1};
    }
    this.environmentId=1;
    %>
    <div >  
    <form>
        <fieldset>   
          <input title="name this node, keep it short!" type="text" name="nodes_dialog_name" id="nodes_dialog_name" value="<%= this.node.name %>"  style="width:70%"/>
          <label for="nodes_dialog_name" class="title">Name</label>
          <textarea title="description of this node" rows="4" cols="25" name="nodes_dialog_description" id="nodes_dialog_description"  style="width:70%"><% this.node.description=$.trim(this.node.description);%><%=this.node.description %></textarea>
          <label for="nodes_dialog_description" class="title">Description</label>
          <input title="recipe being used by this node" type="text" name="nodes_dialog_recipe"  id="nodes_dialog_recipe" value=" " style="width:70%"/>
          <label for="nodes_dialog_recipe" class="title">Recipe</label>
        </fieldset>
      </form>
      <div>
      <div class="title ">Infos</div>
      <div class="leftBlock"> Environment id: <%= this.environmentId %></div>
      <div class="rightblock"> Node id: <%= this.node.id%></div>
    </div>
    
    <button onCLick="pollapli.validateNodeOp('<%= this.mode%>',<%= this.node.id%>)"> <%= this.mode%> </button> 
    </div>
</script> 



<script type="text/x-jqote-template" id="driverTypes_select_tmpl"> 
     <option value=<%=this.driverType%>><%=this.driverType%> driver</option>
</script> 

<script type="text/x-jqote-template" id="driver_dialog_tmpl"> 
   <% if (!this.driver)
    {
      this.driver={driverType:null,options:{'speed':115200}};
    }
    this.environmentId=1;
  %>
    <div>  
    <form>
        <fieldset>  
          <select id="driverType-select">
           </select><button >More info</button> 
        
          <textarea rows="4" cols="25" name="driver_dialog_options" id="driver_dialog_options" class="text ui-state-default ui-corner-all " style="width:95%"><%=JSON.stringify(this.driver.options) %></textarea>
          <label for="driver_dialog_options" class="title">Options</label>
          
        </fieldset>
      </form>

    <button onCLick=""> <%= this.mode%> </button> 
   </div>

 </script> 
 
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
 
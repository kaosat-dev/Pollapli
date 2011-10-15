<script type="text/x-jqote-template" id="editDialog_tmpl"> 
    <% if (!this.node)
    {
      this.node={name:"Default device",description:"This is a default device",type:"...",id:-1};
    }
    this.environmentId=1;
    %>
    <div >  
    <form class="cmxform">
        <fieldset>   
          <legend class="title">Node infos</legend>
            <ol>
             <li>
             Environment id: <%= this.environmentId %>
             </li>
             <li>
             Node id: <%= this.node.id%>
             </li>
           </ol>
        </fieldset>
        <fieldset>   
        <% if(this.driver) { %>
            <div >isPluggedIn: <%=this.driver.isPluggedIn%></div>
            <div >isConnected: <%=this.driver.isConnected%></div>
            <button onclick="pollapli.ui.openDriverDialog(<%=j%>,'modify')">Modify driver </button>
        
      <% }else { %>
         <button onclick="pollapli.ui.openDriverDialog(<%=j%>,'set')">Set driver</button>
       <% }%>
          <legend class="title">Node Settings</legend>
          <ol>
             <li>
              <label  class="title">Name</label>
              <input title="name this node, keep it short!" type="text" name="dialogName" id="dialogName" value="<%= this.name %>" />
             </li>
             <li>
              <label for="nodes_dialog_description" class="title">Description</label>
              <textarea title="description of this node" rows="4" cols="25" name="nodes_dialog_description" id="nodes_dialog_description" ><% this.node.description=$.trim(this.node.description);%><%=this.node.description %></textarea>
             </li>
             <li>
              <label for="deviceRecipe" class="title">Recipe</label>
              <select id="deviceRecipe">
                 <option value='' selected='selected'></option>
                 <option value="">Mendel Reprap: Standard </option>
                 <option value="">Prussa Reprap: Standard </option>
                 <option value="">Makerbot Cupcake: Standard </option>
              </select>
             </li>
             <li>
                <label for="driver" class="title">Driver</label>
                  <select id="deviceDriver">
                   <option value='' selected='selected'></option>
                   <option value="">Teacup driver</option>
                   <option value="">Makerbot driver</option>
                 </select> 
              </li>
         </ol>
        </fieldset>
      </form>
     
      <div>
    
    </div>
    
    <button onCLick="pollapli.validateNodeOp('<%= this.mode%>',<%= this.node.id%>)"> <%= this.mode%> </button> 
    </div>
</script> 

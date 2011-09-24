<script type="text/x-jqote-template" id="nodes_tmpl"> 
    <% var divId="nodediv_"+j+'' ; %>
    <div id="<%=divId%>" class="ui-corner-all ui-state-default " >
      <div name="id" id="id">Id: <%=this.id%></div>
      <div name="name" id="name">Name: <%=this.name%></div>
      <div name="description" id="description">description: <%=this.description%></div>
      
      <% if(this.driver) { %>
            <div >isPluggedIn: <%=this.driver.isPluggedIn%></div>
            <div >isConnected: <%=this.driver.isConnected%></div>
      <% }else 
      { %>
        No driver set
       <% }%>

      <br>
      <a href="#" class="deleteButton ui-priority-primary ui-corner-all ui-state-default block" >Delete <span class="block ui-icon ui-icon-trash "></span></a>
      <a href="#" class="modifyButton ui-priority-primary ui-corner-all ui-state-default block" >Update <span class="block ui-icon ui-icon-arrowreturnthick-1-n"></span></a>
     
    </div>
</script> 


<script type="text/x-jqote-template" id="nodes_dialog_tmpl"> 
    <% if (!this.element)
    {
      this.element={name:"Default device",description:"This is a default device",type:"...",id:-1};
    }
    this.environmentId=1;
    %>
    <div >  
    <% if(this.mode!="delete") { %>
    <form class="cmxform">
        <fieldset>   
          <legend class="title">Node Infos</legend>
          <ol>
             <li>
             Environment id: <%= this.environmentId %>
             </li>
             <li>
             Node id: <%= this.element.id%>
             </li>
             <li>
              <label for="name" class="title">Name</label>
              <input title="name this node, keep it short!" type="text" name="name" id="name" value="<%= this.element.name %>" />
             </li>
             <li>
              <label for="description" class="title">Description</label>
              <textarea title="description of this node" rows="4" cols="25" name="description" id="description" ><% this.element.description=$.trim(this.element.description);%><%=this.element.description %></textarea>
             </li>
         </ol>
        </fieldset>
        <fieldset>   
          <legend class="title">Driver Settings</legend>
          <ol>
               <% if(this.element.driver) { %>
              <li>
               Current: <%= this.element.driver.driverType %>
              </li>
               <li>
                Can be used for device of type: <%= this.element.driver.deviceType%>
              </li>
              <%}%>
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
        <fieldset>   
          <legend class="title">Device structure Settings</legend>
          <ol>
              <li>
              <label for="deviceRecipe" class="title">Recipe</label>
              <select id="deviceRecipe">
                 <option value='' selected='selected'></option>
                 <option value="">Mendel Reprap: Standard </option>
                 <option value="">Prussa Reprap: Standard </option>
                 <option value="">Makerbot Cupcake: Standard </option>
              </select>
             </li>
         </ol>
        </fieldset>
      </form>
      
      <div>
    
    </div>
    <div align="center">
    <a href="#" class="validateButton ui-priority-primary ui-corner-all ui-state-default block" ><%= this.mode%><span class="ui-icon ui-icon-check block"></span></a>
     </div>
      <% }else { %>
       Are you sure you want to delete this node ? this operation is permanent!<br>
       <a href="#" class="validateButton ui-priority-primary ui-corner-all ui-state-default block" >Yes<span class="ui-icon ui-icon-check block"></span></a>
       <a href="#" class="cancelButton ui-priority-primary ui-corner-all ui-state-default block" >No<span class="ui-icon ui-icon-closethick block"></span></a>
      
      <% } %>
    </div>
</script> 



<script type="text/x-jqote-template" id="driverTypes_select_tmpl"> 
     <option value=<%=this.driverType%>><%=this.driverType%> driver</option>
</script> 

<script type="text/x-jqote-template" id="driver_dialog_tmpl"> 
   <% if (!this.driver)
   {
      this.node={name:"Default-device name",description:"This is a default device",type:"...",id:-1};
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
 
 
  <script type="text/x-jqote-template" id="nodes_dialog_old_tmpl"> 
    <![CDATA[    
    <% if (!this.node)
    {
      this.node={name:"Default-device name",description:"This is a default device",type:"...",id:-1};
    }
    
    this.environmentId=1;
  %>
    <div>
    
      
    <form>
        <fieldset>
          <label for="nodes_dialog_name" class="title">Name</label>
          <input type="text" name="nodes_dialog_name" id="nodes_dialog_name" value="<%= this.node.name %>" class="text ui-state-default ui-corner-all" style="width:95%"/>
          <label for="nodes_dialog_description" class="title">Description</label>
          <textarea rows="4" cols="25" name="nodes_dialog_description" id="nodes_dialog_description" class="text ui-state-default ui-corner-all " style="width:95%"><% this.node.description=$.trim(this.node.description);%><%=this.node.description %></textarea>
          <label for="nodes_dialog_recipe" class="title">Recipe</label>
          <input type="text" name="nodes_dialog_recipe" id="nodes_dialog_recipe" value=" " class="text ui-state-default ui-corner-all" style="width:95%"/>
        </fieldset>
      </form>
      <div>
      <div class="title ">Infos</div>
      <div class="leftBlock"> Environment id: <%= this.environmentId %></div>
      <div class="rightblock"> Node id: <%= this.node.id%></div>
    </div>
      

    <button onCLick=pollapli.validateNodeOp('<%= this.mode%>',<%= this.node.id%>);> <%= this.mode%> </button> 
    </div>
    ]]>
  </script> 
  
  
 <script type="text/x-jqote-template" id="nodes_old_tmpl"> 
    <![CDATA[
    <li>
        <Strong>Device Id:</Strong> <%= this.id %>  <Strong>Name: </Strong><%= this.name %> <Strong>description: </Strong> <%= this.description %><Strong>type: </Strong> <%= this.type %>  <Strong>link: </Strong> <a href=<%= this.link.href %>> <%= this.link.href %></a>      
        <div><button onClick= pollapli.ui.openNodeDialog_test(<%=j%>,"modify") > Modify</button> <button onClick= manager.deleteNode(<%=this.id%>) > Delete</button> </div>   
     </li>
    ]]>
  </script> 
 
 
 <script type="text/x-jqote-template" id="nodes_test_tmpl"> 
    <![CDATA[
    <% this.divId="nodes_test_"+this.id; alert(this.divId);%>
    <div id=<%=this.divId%>>
        <%this.truc=JSON.stringify(this);%>
        <Strong>Name: </Strong> <%=this.name  %>  <Strong>Description: </Strong><%= this.description %> 
        <% $(this.divId).link(this);%>
     </div>
    ]]>
</script> 

 <script type="text/x-jqote-template" id="nodes_deleteDialog_tmpl"> 
    <![CDATA[
    <div>
      Are you sure you want to delete this node ? this operation is permanent!<br>
      <button>Yes</button><button>No</button>
     </div>
      
    ]]>
</script> 
 
<script type="text/x-jqote-template" id="nodes_tmpl"> 
    <% var divId="nodediv_"+j+'' ; %>
    <div id="<%=divId%>" class="ui-corner-all ui-state-default ">
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
       <% if(this.recipe) { %>
           
            <button onclick="pollapli.ui.openRecipeDialog(<%=j%>,'modify')">Modify recipe </button>
        
      <% }else { %>
         <button onclick="pollapli.ui.openRecipeDialog(<%=j%>,'set')">Set recipe</button>
       <% }%>
       
      <br>
      <a href="#" class="deleteButton ui-priority-primary ui-corner-all ui-state-default block" onCLick=manager.deleteNodeTest(<%=this.id%>)>Delete <span class="ui-icon ui-icon-trash "></span></a>
      <button class="deleteButton ui-priority-primary ui-corner-all ui-state-default" onCLick=manager.deleteNodeTest(<%=this.id%>)>Delete <span class="ui-icon ui-icon-trash "></span></button>
      <button class="modifyButton ui-priority-primary ui-corner-all ui-state-default" onClick=pollapli.ui.openNodeDialog_test(<%=j%>,"modify") > Update <span class="ui-icon ui-icon-arrowthick-1-n "></button>
      
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
 
 
  <script type="text/x-jqote-template" id="nodes_dialog_old_tmpl"> 
    <![CDATA[
    
      
    
    <% if (!this.node)
    {
      this.node={name:"...",description:"...",type:"...",id:-1};
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
        <div><button onClick= pollapli.openNodeDialog(<%=j%>,"modify") > Modify</button> <button onClick= manager.deleteNode(<%=this.id%>) > Delete</button> </div>   
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
 
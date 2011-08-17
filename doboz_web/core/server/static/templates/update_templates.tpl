<script type="text/x-jqote-template" id="updates_tmpl"> 
          <![CDATA[
                 
          <div class=" leftBlock ui-widget-content ui-corner-all " style="margin:7px 0px 20px 0px; width:99%">
            
            <div class="  ui-widget-header   ui-corner-tr ui-corner-tl " >
            <table><tr><td>  <%=this.type %>:</td> <td class="title"><%= this.name %> </td></tr></table>
            </div>
            <div class="leftBlock "  style="width:30%"   >
                <div class="leftBlock "  style="margin:10px 70px 10px 20px;"><img  width="320" height="200" alt=<%= this.img %> src=<%= this.img %> /> </div>
            </div>
            <div  class="leftBlock "  style="width:50%; margin:10px 0px 0px 0px; "  >
                <table  class="fullWidth tableTest"> 
                    <tr >
                        <td class="title ui-widget-header " > Description </td>
                    </tr>
                    <tr>
                        <% this.description=this.description.replace(/\r?\n|\r/g, "<br/>");%>
                        <td ><%= this.description %></td>
                    </tr>   
                    <tr>
                        <td class="title ui-widget-header  " > Tags </td>
                    </tr>
                    <tr>
                        <td ><%= this.tags.items %></td>
                    </tr>
                      <tr>
                        <td class="title ui-widget-header  " > Version </td>
                    </tr>
                    <tr>
                        <td ><%= this.version %></td>
                    </tr>
                     <tr >
                        <td class="title ui-widget-header" > Download & install </td>
                      </tr>  
                      <tr  >
                        <td> 
                           <% var progressbarDivId="progbardiv_"+j+'' ;%>

                            <% if(!this.downloaded) { %>
                            <button onClick="manager.postUpdateDownload()">Download & Install </button>
                         
                         
                             <divclass="progresswraper " >
                            <div id=<%=progressbarDivId%> class="progressbar " style="position:relative;height:1.1em">
                              <span class="pblabel">0%</span> 
                            </div>
                            </div>
                         <% }else{ %>
                           This update is alread installed & up to date!
                           <%}%>
                       
                         
                        
                          </td> 
                      </tr>

                </table>
            </div>            
          </div>
         
                ]]>
  </script> 
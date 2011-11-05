 <script type="text/x-jqote-template" id="files_list_tmpl">
<![CDATA[

      <% 
      var dt=new Date((Number(this.created))*1000);    
      var convTime=(dt.getMonth()+1)+ '/'+dt.getDate()+ '/'+dt.getFullYear() +" "+ dt.getHours() + ':' + dt.getMinutes() + ':' + dt.getSeconds() ;
      var created=convTime;
      
      var dt=new Date((Number(this.modified))*1000);    
      var convTime=(dt.getMonth()+1)+ '/'+dt.getDate()+ '/'+dt.getFullYear() +" "+ dt.getHours() + ':' + dt.getMinutes() + ':' + dt.getSeconds() ;
      var modified=convTime;
      %>
      <ul>Name:<%= this.name %>  Size: <%= this.size %> Created: <%= created %>  Modified:<%=modified%> <button onClick=pollapli.ui.deleteFile('<%= this.name %>')>Delete</button> </ul>
    ]]>
 </script>
<script type="text/x-jqote-template" id="files_tmpl">
<![CDATA[
    Files:
    <li id="_filesLi">
    
    
    </li>
     <button onClick=manager.deleteFiles()>Delete All</button> </ul>
    ]]>
 </script>


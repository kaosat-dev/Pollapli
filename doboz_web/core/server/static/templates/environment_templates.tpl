  
  <script type="text/x-jqote-template" id="environments_tmpl">
<![CDATA[

    <li>
      <Strong>Name </Strong><%= this.name %> <Strong>Description </Strong> <%= this.description %> <Strong>Status </Strong> <%= this.status %> <Strong>link: </Strong> <a href=<%= this.link.href %>> <%= this.link.href %></a> 
      <ul >
        <li class="title">Nodes:</li>
        <div><button onClick=pollapli.ui.openNodeDialog_test(-1,"create")> Add</button> </div>
          <ol id="nodes">
           
          </ol>
      </ul>
      <ul >
        <li class="title">Tasks:</li>
          <ol id="tasks">
          </ol>
      </ul>
    </li>

    ]]>
  </script>
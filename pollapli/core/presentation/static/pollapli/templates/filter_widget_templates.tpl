<script type="text/x-jqote-template" id="filter_widget_tmpl"> 
    <div id="filterControl" class="leftBlock ui-widget-content ui-widget-header ui-corner-all " style="margin:2px 0px 2px 0px; width:99%;float:left">
    Order by:
    <select id="criteriaSelect">
      <option value='' selected='selected'></option>
      <%  $.each(this.orderables,  function(key,value)
         {
          %>
          <option value=<%= value %>> <%= value %> </option>
        <% });
         %>  
    </select>&nbsp;&nbsp;&nbsp;&nbsp;
    Filter by:
    <%  $.each(this.filterables,  function(key,value)
         {
          %>
          <input id=<%= value %> type="checkbox" name=<%= value %> value="downloaded" /> <%= value %>
        <% });
     %>    
     <button id="clearFiltersButton">Clear </button>
   </div>
</script> 

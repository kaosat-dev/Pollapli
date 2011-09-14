var NodesView= Backbone.View.extend
(
  {
    initialize: function() 
    {
      this.template=this.options.template;
      if (this.template==null)
      {
        this.template=pollapli.ui.templates["nodes_tmpl"];
      }
      _.bindAll(this, "render","open_EditDialog");
      this.collection.bind("all", this.render,this);
      this.render();
      
    },
    render: function() 
    {
      $(this.el).html("");
      $(this.el).jqotesub(this.template, this.collection.toJSON());
      return this;
    },
    add: function () 
    {
        $("#new-zone-form-dialog").dialog("open");
    },
    open_EditDialog : function(e)
    {
        $("#nodeDialog").dialog({autoOpen: false}); 
        $("#nodeDialog" ).dialog( "option", "title", "update node " );
     // $('#node-dialog').dialog({show: 'slide' , title:" node"});
        $('#nodeDialog').jqotesub(pollapli.ui.templates.nodes_dialog_tmpl, {'node':null,'mode':'update'});  
        $("#nodeDialog button").button();
        $('#nodeDialog').dialog('open');
    }
    ,
    events: 
    {
        "click button": "open_EditDialog"
    },
    
  }
);
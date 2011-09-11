var NodesView= Backbone.View.extend
(
  {
    events: {
        "click #new-zone-button": "add"
    },
    initialize: function() 
    {
      this.template=this.options.template;
      if (this.template==null)
      {
        this.template=pollapli.ui.templates["nodes_tmpl"];
      }
      _.bindAll(this, "render","add");
      this.collection.bind("all", this.render,this);
      this.render();
      
    },
    render: function() 
    {
      $(this.el).jqotesub(this.template, this.collection.toJSON());
      return this;
    },
     add: function () 
     {
        $("#new-zone-form-dialog").dialog("open");
    }
  }
);
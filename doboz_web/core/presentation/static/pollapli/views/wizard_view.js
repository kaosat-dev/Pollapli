var WizardView= Backbone.View.extend
(
  {
    initialize: function() 
    {
      this.template=this.options.template;
      if (this.template==null)
      {
        this.template=pollapli.ui.templates["header_tmpl"];
      }
      _.bindAll(this, "render","navigate");
      this.render();
    },
    render: function() 
    {
      $(this.el).jqotesub(this.template, null);  
      
      return this;
    },
    navigate: function () 
    {
       
    },
    events: 
    {
        "click": "navigate"
    },
  }
);
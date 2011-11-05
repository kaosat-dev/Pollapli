var HeaderView= Backbone.View.extend
(
  {
    initialize: function() 
    {
      this.template=this.options.template;
      this.page={pageName:"UPDATES"};
      if (this.template==null)
      {
        this.template=pollapli.ui.templates["header_tmpl"];
      }
      _.bindAll(this, "render","navigate");
     
      this.render();
    },
    render: function() 
    {
      $(this.el).jqotesub(this.template,this.page);  
      
      return this;
    },
    navigate: function (e) 
    {
      //alert($(e.currentTarget).attr('id'));
      this.page={pageName:$(e.currentTarget).attr('id').toUpperCase()};
      this.render();
    },
    events: 
    {
        "click img": "navigate"
    },
  }
);
var PageView= Backbone.View.extend
(
  {
    initialize: function() 
    {
      this.template=this.options.template;
      if (this.template==null)
      {
        this.template=pollapli.ui.templates["basePage_tmpl"];
      }
      
      this.collection.bind("all", this.render,this);
      this.render();
      
    },
    render: function() 
    {
      $(this.el).jqotesub(this.template, this.collection.toJSON());
      return this;
    }
   
  }
);
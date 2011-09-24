var EditView= Backbone.View.extend
(
  {
    initialize: function() 
    {
      this.template=this.options.template;
      if (this.template==null)
      {
        this.template=pollapli.ui.templates["editDialog_tmpl"];
      }
      _.bindAll(this, "render","changed");   
    },
    render : function()
    {
       $(this.el).jqotesub(this.template, this.model.toJSON());
      return this;
    },
     changed:function(e) 
     {
       var changed = e.currentTarget;
       var value = $("#"+changed.id).val();
       var obj = "{\""+changed.id +"\":\""+value+"\"}";
       var objInst = JSON.parse(obj);
       this.model.set(objInst);            
    },
    events : 
    {
        "change input" :"changed",
        "change select" :"changed"
    },
  }
);
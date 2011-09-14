function get_type(thing)
{
    if(thing===null)return "[object Null]"; // special case
    return Object.prototype.toString.call(thing);
}
var EventsView= Backbone.View.extend
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
        this.template=pollapli.ui.templates["events_tmpl"];
      }
      _.bindAll(this, "render","add");
      if (this.collection!=null)
      {
      this.collection.bind("all", this.render,this);
      }
      
      
    },
    render: function() 
    {
      if (this.collection!=null)
      {
        var latestFirst = this.collection.sortBy(function(event) 
        {
          return -event.get("time");
        });
  
        latestFirst=jQuery.parseJSON(JSON.stringify(latestFirst) ); 
        $(this.el).jqotesub(this.template, latestFirst);
      }
      return this;
    },
     add: function () 
     {
        $("#new-zone-form-dialog").dialog("open");
    }
  }
);

var EventsHeaderView= Backbone.View.extend
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
        this.template=pollapli.ui.templates["events_tmpl"];
      }
      _.bindAll(this, "render","add");
      if (this.collection!=null)
      {
      this.collection.bind("all", this.render,this);
      }
      
      
    },
    render: function() 
    {
      if (this.collection!=null)
      {
        var latestFirst = this.collection.sortBy(function(event) 
        {
          return -event.get("time");
        });
  
        latestFirst=jQuery.parseJSON(JSON.stringify(latestFirst) ); 
        $(this.el).jqotesub(this.template, latestFirst);
      }
      return this;
    },
     add: function () 
     {
        $("#new-zone-form-dialog").dialog("open");
    }
  }
);

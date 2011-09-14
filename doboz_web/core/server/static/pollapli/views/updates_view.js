function get_type(thing)
{
    if(thing===null)return "[object Null]"; // special case
    return Object.prototype.toString.call(thing);
}

function displayProperties(obj)
{
   var list="";
   for(var p in obj)
   list += p + " : " + obj[p] + "<br>";
   console.log(list);
}

var UpdatesView= Backbone.View.extend
( 
   {
    initialize: function() 
    {
      
      
      this.filterView=new FilterView({el: $("#truc"),orderables:["name","version","type"],filterables:["downloaded","installed",] });//,{orderables:["name","version","type"],filterables:["downloaded","installed",]});
      this.filterView.parent=this;

      //this.updateListView=new UpdatesListView({collection: this.collection, el: $("#machin") });
      
      _.bindAll(this, "render");
      this.collection.bind("all", this.render,this);   
      $(this.el).trigger('totoEvent');
    },
    renderList : function(updates)
    {
      $("#machin").html("");
      updates.each(function(update)
      {
        var view = new UpdateView({model: update});
        $("#machin").append(view.render().el);
      });
      return this;
    },
    render : function()
    {
        $(this.el).html("");
        this.el.append($("<div id='truc'></div>", {id: "#truc"}));
        this.el.append($("<div id='machin'>dfgdfg</div", {id: "#machin"}));
        this.filterView.render();
        this.renderList(this.collection);
     
    },
    tutu : function()
    {
      $(this.el).trigger('totoEvent');
      alert("child event tutu raised inside update view");
      
    },
    events: 
    {
       'tutuEvent': 'tutu'
    },
    
   }
);

var UpdateView= Backbone.View.extend
(
  {
    initialize: function() 
    {
      this.template=pollapli.ui.templates["updates_tmpl"];
      $('.progressbar').progressbar({value:0});
     // _.bindAll(this, "render");
     // this.model.bind("all", this.render,this);
    },
    render: function() 
    {
      $(this.el).jqotesub(this.template, this.model.toJSON());
      //needs to reference only the progressbars inside of this el
      //this.$(".title")
      /*$(' .progressbar').progressbar(
      {
         value: 0,
         change: function(event, ui) 
         {
            var newVal = $(this).progressbar('option', 'value');
            $('.pblabel', this).text(newVal + '%');
          }
        });
        pollapli.ui.set_progressbar=function(divName,percent)
{
  $(divName).progressbar( "option", "value", percent); 
}
        */
      return this;
    }
   }
);

var UpdatesListView= Backbone.View.extend
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
        this.template=pollapli.ui.templates["updates_tmpl"];
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
       
       // $(this.el).jqotesub(this.template, this.collection.toJSON());
        //this.el.append($("<div id='truc'></div>", {id: "#truc"}));
        //this.el.append($("<div id='machin'>dfgdfg</div", {id: "#machin"}));
        
        $("#machin").jqotesub(this.template, this.collection.toJSON());
        //$(this.el).jqotesub(this.template, this.collection.toJSON());
        //$(this.el+"> div[id=machin]").jqotesub(this.template, this.collection.toJSON());
      }
      return this;
    },
     add: function () 
     {
        $("#new-zone-form-dialog").dialog("open");
    }
  }
);
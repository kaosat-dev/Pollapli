 var FilterView= Backbone.View.extend
(
  {
    initialize: function() 
    {
      this.template=pollapli.ui.templates["filter_widget_tmpl"];
      this.filterables=this.options.filterables;
      this.orderables=this.options.orderables;
      this.currentOrder="name";
      this.filterParams={};
      _.bindAll(this, "render");

      // $("#truc").jqotesub(pollapli.ui.templates["filter_widget_tmpl"], {orderables:["name","version","type"],filterables:["downloaded","installed",]});
      
    },
    render: function() 
    {  
     $(this.el).jqotesub(this.template, {orderables:this.orderables,filterables:this.filterables});
      return this;
    },
    order : function(e)
    {
      var sortParam=this.$('[id=criteriaSelect]').val();
      this.$('[id=criteriaSelect]').val("0");
      if(this.currentOrder!=null)
      {
        if(this.currentOrder==sortParam)
        {
          this.currentOrder="-"+this.currentOrder;
        }
        else
        {
          this.currentOrder=sortParam;
        }
      }
      else
      {
        this.currentOrder=sortParam;
      }
      
      this.parent.renderList(this.parent.collection.filterAndOrder(this.filterParams,this.currentOrder));
     // this.parent.renderList(this.parent.collection.sortByParam(this.currentOrder));
    },
    filter : function(e)
    {
      var checked={};
      $('#filterTruc input').each(function() 
      {
        checked[$(this).attr('name')]=$(this).prop("checked") ;
      });
      this.filterParams=checked;
      this.parent.renderList(this.parent.collection.filterAndOrder(this.filterParams,this.currentOrder));
       
    },
    clearFilters : function()
    {
      this.filterParams={};
      $('#filterTruc input').each(function() 
      {
          $(this).prop("checked",false) ;
      });
      this.parent.renderList(this.parent.collection.filterAndOrder(this.filterParams,this.currentOrder));
    },
    doClick : function(e)
    {  
      alert("kljlk")    ;
    },
    events: 
    {
       'change select ' : 'order',
       'click input': 'filter',  
       'click #clearFiltersButton': 'clearFilters'
    },
   }
);
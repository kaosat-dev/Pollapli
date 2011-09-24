var Node = Backbone.Model.extend(
{
    urlRoot : pollapli.mainUrl+'rest/environments/1/nodes',
   
            initialize: function()
            {  
              
            },
            defaults: 
            {
                name: 'Default node',
                description: 'just a node',
            }
});
var NodeCollection = Backbone.Collection.extend(
{
  model : Node,
  url: pollapli.mainUrl+'rest/environments/1/nodes',
  parse: function(response) 
  {
    return response.nodes.items;
  },
  comparator : function(node)
  {
    return node.get("id");
  },
  justATest : function(longPollEvent)
  {
    alert("node collection got event from longpoll: "+longPollEvent.eventType+longPollEvent.targetElement+" "+longPollEvent.targetElementId+"data "+longPollEvent.data);
    if(longPollEvent.eventType=="node_created")
    {
      var found=this.detect(function(id){ node.get("id")==id})
      //var bidule=found()
      //this.detect (obj) -> (obj.get('product').get('id') == pid)
      /*longPollEvent.data.id
      truc=
      
       if(longPollEvent.data.id)
      {
        
      }*/
      
    }
    
   
  },
  sortByParam : function(param)
  {
    var result = _(this.sortBy(function(node) 
        {
          //workeround for inverted compare (includes handling of strings)
          if( param.indexOf("-") != -1)
          {     
             tmp=node.get(param.substr(1));
             if(is('String', tmp))
             {
               return -tmp.charCodeAt(0);
             }
             else
             {
               return -tmp
             }
          }
          else
          {
             return node.get(param);
          }
         
        }));
     return result;
  },
  filterByParam : function(params)
  {
    //need a look at the "all" underscore js method
    var result= _(this.filter(function(node)
    {
     valid=true;
     _.each(params, function(value, key)
     { 
       console.log("node: "+node.get("name")+ " key: "+key +" node var value: "+update.get(key)+" val: "+value);
        if(update.get(key)!=value)
        {
          valid=false; 
        }
     });
      return valid;
    }));
    return result;
  },
  filterAndOrder : function(filterParams,sortParam)
  {
    var result=_(this.chain()
    .sortBy(function(node)
    {
       //workaround for inverted compare (includes handling of strings)
          if( sortParam.indexOf("-") != -1)
          {     
             tmp=node.get(sortParam.substr(1));
             if(is('String', tmp))
             {
               return -tmp.charCodeAt(0);
             }
             else
             {
               return -tmp
             }
          }
          else
          {
             return node.get(sortParam);
          }
         
    })
    .filter(function(node)
    {
       valid=true;
     _.each(filterParams, function(value, key)
     { 
       
        if(node.get(key)!=value )
        {
          valid=false; 
        }
     });
      return valid;
    }));
    result=result.value();
    return result 
  }
  
});
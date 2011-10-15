var Node = Backbone.Model.extend(
{
    urlRoot : pollapli.mainUrl+'rest/environments/1/nodes',
    initialize: function()
    {  
        //this.driver=new Driver({url:this.url+"/driver"});
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
  
  initialize: function()
  {  
    _.bindAll(this, "justATest");  
  },
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
    if(longPollEvent.eventType=="node_created" || longPollEvent.eventType=="node_updated" || longPollEvent.eventType=="node_deleted")
    {
      this.fetch();
      /*try
      {
        console.log("Element id: "+longPollEvent.data.id);
        var refId=longPollEvent.data.id;
        var foundNode=this.detect(function(node){return node.get("id")==refId;})
        console.log("Found item"+foundNode);
        if(foundNode==undefined)
        {
          console.log("new item");
          this.add(new Node(data));
        }
      }
      catch(error)
      {
        console.log("error"+error);
      }*/
    }
    
   
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
                tmp=tmp.toLowerCase();
               return -tmp.charCodeAt(0);
             }
             else
             {
               return -tmp
             }
          }
          else
          {
             tmp=node.get(sortParam)
             if(is('String', tmp))
             {
                tmp=tmp.toLowerCase();
               return tmp.charCodeAt(0);
             }
             else
             {
               return tmp
             }
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
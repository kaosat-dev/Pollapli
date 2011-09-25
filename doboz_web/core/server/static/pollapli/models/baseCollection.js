var BaseCollection = Backbone.Collection.extend(
{
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
var BaseCollection = Backbone.Collection.extend(
{
  sortByParam : function(param)
  {
    var result = _(this.sortBy(function(baseModel) 
        {
          //workeround for inverted compare (includes handling of strings)
          if( param.indexOf("-") != -1)
          {     
             tmp=baseModel.get(param.substr(1));
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
             return baseModel.get(param);
          }
         
        }));
     return result;
  },
  filterByParam : function(params)
  {
    //need a look at the "all" underscore js method
    var result= _(this.filter(function(baseModel)
    {
     valid=true;
     _.each(params, function(value, key)
     { 
       console.log("baseModel: "+baseModel.get("name")+ " key: "+key +" baseModel var value: "+baseModel.get(key)+" val: "+value);
        if(baseModel.get(key)!=value)
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
    .sortBy(function(baseModel)
    {
       //workaround for inverted compare (includes handling of strings)
          if( sortParam.indexOf("-") != -1)
          {     
             tmp=baseModel.get(sortParam.substr(1));
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
             return baseModel.get(sortParam);
          }
         
    })
    .filter(function(baseModel)
    {
       valid=true;
     _.each(filterParams, function(value, key)
     { 
       
        if(baseModel.get(key)!=value )
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
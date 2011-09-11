function is(type, obj) 
{
    var clas = Object.prototype.toString.call(obj).slice(8, -1);
    return obj !== undefined && obj !== null && clas === type;
}

var UpdateStatus = Backbone.Model.extend(
{
  
});

var Update = Backbone.Model.extend(
{
  urlRoot : pollapli.mainUrl+'rest/config/updates/1',
  initialize: function()
  {        
    /*
       var data={"start":true}
  data=JSON.stringify(data);
  this.postData(manager.mainUrl+"rest/config/updates/"+updateId+"/status",'application/pollapli.update.status+json',data,
     */
  },
  defaults: 
  {
     id:-1,
     type:null,
     name: 'an update',
     description: 'description',
     version:'0.0.0',
     downloaded:false,
     installed:false,
     img: '',
     tags:''
  }
  
});

var Updates = Backbone.Collection.extend(
{
  model : Update,
  url: pollapli.mainUrl+'rest/config/updates',
  parse: function(response) 
  {
    //alert(JSON.stringify(response.updates.items));
    return response.updates.items;
  },
  comparator : function(update)
  {
    return update.get("type");
  },
  sortByParam : function(param)
  {
    var result = _(this.sortBy(function(update) 
        {
          //workeround for inverted compare (includes handling of strings)
          if( param.indexOf("-") != -1)
          {     
             tmp=update.get(param.substr(1));
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
             return update.get(param);
          }
         
        }));
     return result;
  },
  filterByParam : function(params)
  {
    //need a look at the "all" underscore js method
    var result= _(this.filter(function(update)
    {
     valid=true;
     _.each(params, function(value, key)
     { 
       console.log("update: "+update.get("name")+ " key: "+key +" update var value: "+update.get(key)+" val: "+value);
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
    .sortBy(function(update)
    {
       //workaround for inverted compare (includes handling of strings)
          if( sortParam.indexOf("-") != -1)
          {     
             tmp=update.get(sortParam.substr(1));
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
             return update.get(sortParam);
          }
         
    })
    .filter(function(update)
    {
       valid=true;
     _.each(filterParams, function(value, key)
     { 
       
        if(update.get(key)!=value )
        {
          valid=false; 
        }
     });
      return valid;
    }));
   
 
    result=result.value();

   /* var youngest = _(stooges).chain()
  .sortBy(function(stooge){ return stooge.age; })
  .map(function(stooge){ return stooge.name + ' is ' + stooge.age; })
  .first()
  .value();
  */
    return result 
  }
  
  
});
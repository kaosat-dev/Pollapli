var Node = Backbone.Model.extend(
{
    urlRoot : pollapli.mainUrl+'rest/environments/1/nodes',
   
            initialize: function()
            {  
              
            },
            defaults: 
            {
                name: 'Default environment',
                description: 'just an environment',
            }
});
var NodeCollection = Backbone.Collection.extend(
{
  model : Node,
  url: pollapli.mainUrl+'rest/environments/1/nodes',
  parse: function(response) 
  {
    return response.nodes.items;
  }
});
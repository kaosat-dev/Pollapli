var Task = Backbone.Model.extend(
{
    urlRoot : pollapli.mainUrl+'rest/environments/1/tasks',
   
            initialize: function()
            {  
              
            },
            defaults: 
            {
                name: 'Default Task',
                description: 'just a task',
            }
});
var TaskCollection = Backbone.Collection.extend(
{
  model : Task,
  url: pollapli.mainUrl+'rest/environments/1/tasks',
  parse: function(response) 
  {
    return response.tasks.items;
  }
});
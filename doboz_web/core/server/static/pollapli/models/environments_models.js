var Environment = Backbone.Model.extend(
{
    urlRoot : pollapli.mainUrl+'rest/environments',
            initialize: function()
            {  
              this.nodes=new NodeCollection();
              this.tasks=new TaskCollection();
              this.nodes.url=pollapli.mainUrl+"rest/environments/"+this.id+"/tasks";
              this.tasks.url=pollapli.mainUrl+"rest/environments/"+this.id+"/nodes";
            },
            defaults: 
            {
                name: 'Default environment',
                description: 'just an environment',
                status:'frozen',
                
            }
});

var EnvironmentCollection = Backbone.Collection.extend(
{
  model : Environment,
  url: pollapli.mainUrl+'rest/environments',
  parse: function(response) 
  {
    return response.environments.items;
  },
  frozen : function() 
  {
    return this.filter(function(environment) 
    {
      return environment.get('status') == 'frozen';
    });
  }
});

pollapli.backbone={}


var Environment = Backbone.Model.extend(
{
    urlRoot : pollapli.mainUrl+'rest/environments',
            initialize: function()
            {  
            },
            defaults: 
            {
                name: 'Default environment',
                description: 'just an environment',
                status:'frozen'
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


var EnvironmentView= Backbone.View.extend
(
  {
    tagName:  "li",
    initialize: function() 
    {
      this.model.bind('change', this.render, this);
      this.model.bind('destroy', this.remove, this);
    },
    render: function() 
    {
      $(this.el).jqotesub(pollapli.ui.templates.nodes_tmpl,manager.nodes);
      return this;
    }
  
    //$('#testDiv_nodes button').button();  
  

  }
);


////////////////////////////////////////
pollapli.backbone.truc=function(res)
{
 // alert("success"+JSON.stringify(res));
 alert("envs"+JSON.stringify(pollapli.backbone.envs));
 var anEnv = pollapli.backbone.envs.get(1);
 alert("anEnv"+JSON.stringify(anEnv));
}



pollapli.backbone.addNode=function()
{

   var sndNode=pollapli.backbone.nodes.add({name: "tuturulutyutut",description: "William Shakespeare"});
   pollapli.backbone.removeNode();
}

pollapli.backbone.removeNode=function()
{
   pollapli.backbone.nodes.remove({id: 34});
}


pollapli.backbone.sucess=function()
{
  alert("sucess")
}
pollapli.backbone.error=function()
{
  alert("error")
}



pollapli.backbone.init=function()
{
     
  
  this.envs=new EnvironmentCollection();
  this.envs.fetch({success :pollapli.backbone.sucess, error: pollapli.backbone.error}); 
  
  
  this.nodes=new NodeCollection();
  this.nodes.bind("add", function(node) 
  {
    alert("Added " + node.get("name") + "!");
    node.save({success :pollapli.backbone.sucess, error: pollapli.backbone.error});
  });
  
  this.nodes.bind("remove", function(node) 
  {
    
    alert("Removed " + node.get("name") + "with id"+node.get("id") +"!");
    node.destroy({success :pollapli.backbone.sucess, error: pollapli.backbone.error});
  });
  
  this.nodes.fetch({success :pollapli.backbone.addNode, error: pollapli.backbone.truc2}); 
  //this.envs.reset({success :pollapli.backbone.truc, error: pollapli.backbone.truc2});

}
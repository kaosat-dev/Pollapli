pollapli.backbone={}

var MainRouter = Backbone.Router.extend(
{
  routes : 
  {
    "overview/:something" : "openInterfacePage",
    "structure/:something" : "openInterfacePage",
    "tasks/:something" : "openInterfacePage",
    "data/:something" : "openInterfacePage",
    "tools/:something" : "openInterfacePage",
    "config/:something" : "openInterfacePage",
    "pages/:updates" : "openInterfacePage",
    "help/:something" : "openInterfacePage",
  },
 
  openInterfacePage : function(something) 
  {
   // alert(something);
   // this.document.pages.at(something).open();
    this.navigate("pages/" + something);
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
  // pollapli.backbone.removeNode();
}

pollapli.backbone.removeNode=function()
{
   pollapli.backbone.nodes.remove({id: 34});
}


pollapli.backbone.sucess=function()
{
  
  console.log("sucess");
}
pollapli.backbone.error=function()
{
  console.log("error");
}

var EnvironmentView= Backbone.View.extend
(
  {
    //
    initialize: function() 
    {
      this.template=this.options.template;
      if (this.template==null)
      {
        this.template=pollapli.ui.templates["environments_tmpl_simple"];
      }
      
      //_.bindAll(this, "render", "add");
      _.bindAll( this, 'render' )
      this.collection.bind("all", this.render,this);
      this.render();
      
    },
    render: function() 
    {

      $(this.el).jqotesub(this.template, this.collection.toJSON());
      return this;
    }
  }
);

var NodesView= Backbone.View.extend
(
  {
    events: {
        "click #new-zone-button": "add"
    },
    initialize: function() 
    {
      this.template=this.options.template;
      if (this.template==null)
      {
        this.template=pollapli.ui.templates["nodes_tmpl"];
      }
      _.bindAll(this, "render","add");
      this.collection.bind("all", this.render,this);
      this.render();
      
    },
    render: function() 
    {
      $(this.el).jqotesub(this.template, this.collection.toJSON());
      return this;
    },
     add: function () 
     {
        $("#new-zone-form-dialog").dialog("open");
    }
  }
);

var InterfacePageView= Backbone.View.extend
(
  {
    initialize: function() 
    {
      this.template=this.options.template;
      if (this.template==null)
      {
        this.template=pollapli.ui.templates["nodes_tmpl"];
      }
      
      this.collection.bind("all", this.render,this);
      this.render();
      
    },
    render: function() 
    {
      $(this.el).jqotesub(this.template, this.collection.toJSON());
      return this;
    }
   
  }
);

pollapli.backbone.init=function()
{
  
  this.envs=new EnvironmentCollection();
  this.nodes=new NodeCollection();
  
  this.environmentView = new EnvironmentView({collection: this.envs, el: $("#backboneTest"),template: pollapli.ui.templates["environments_tmpl_simple2"]}); 
  this.nodesView = new NodesView({collection: this.nodes, el: $("#backboneTest2") }); 
  

  
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
  
  
  this.envs.fetch({success :pollapli.backbone.sucess, error: pollapli.backbone.error}); 
  this.nodes.fetch({success :pollapli.backbone.sucess, error: pollapli.backbone.truc2}); 
  //this.envs.reset({success :pollapli.backbone.truc, error: pollapli.backbone.truc2});
  
  this.router=new MainRouter();
  Backbone.history.start();
}



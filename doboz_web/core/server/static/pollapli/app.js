pollapli={}
pollapli.app={}
pollapli.mainUrl="http://"+window.location.host+"/"

pollapli.ui={}
pollapli.ui.templates={};


////////helpers
function S4() {
   return (((1+Math.random())*0x10000)|0).toString(16).substring(1);
}
function guid() {
   return (S4()+S4()+"-"+S4()+"-"+S4()+"-"+S4()+"-"+S4()+S4()+S4());
}




pollapli.clientId=guid();


//method for loading and compiling all templates:
//upon completion, the callback function is fired
pollapli.ui.loadTemplates=function(callback)
{
   var templateUrl="pollapli/templates/"; 
   var templates=['header_template.tpl','filter_widget_templates.tpl','file_templates.tpl', 'environment_templates.tpl','event_templates.tpl','update_templates.tpl','node_templates.tpl','page_templates.tpl'  ];
   
   var onAllLoaded = function(){console.log("finished compiling templates");callback()};
   var afterFunction = _.after(templates.length, onAllLoaded);
  
   var templateCompiler=function(templateName)
   {
     $.get(templateUrl+templateName, 
      function(doc) 
      {
          var tmpls = $(doc).filter('script');
          tmpls.each(function() 
          {
              try
              {
                pollapli.ui.templates[this.id] = $.jqotec(this);
              }
              catch(error)
              {
                console.log("error: "+error+" while loading template"+this.id + " in file: "+templateUrl+templateName);
              }
              
          });
          console.log("finished compiling template file: "+templateUrl+templateName); 
          afterFunction();
      });
    }
    _.each(templates, templateCompiler); 
}

//method for dynamically loading and script files
//upon completion, the callback function is fired
pollapli.loadScripts=function(callback)
{
    var dependencies=
    ['models/pages_models.js','routers/main_router.js','views/header_view.js','views/page_view.js','models/nodes_models.js',
    'views/filter_view.js','models/updates_models.js','views/updates_view.js','models/events_models.js','views/events_view.js',
    'models/pages_models.js','views/node_view.js','models/nodes_models.js'
    ];  
    var onAllLoaded = function(){console.log("finished loading scripts");callback();};
    var afterFunction = _.after(dependencies.length, onAllLoaded);
    
    var scriptLoader=function(scriptName)
    {
      try
      {
        $.getScript("pollapli/"+scriptName,this.initMain);
      }
      catch(error)
      {
        console.log("error: "+error+" while loading script"+scriptName );
      }
       afterFunction();
    }
    
    _.each(dependencies, scriptLoader); 
}


var App = 
{
    
    Views: {},
    Routers: {},
    init: function() 
    { 
       pollapli.loadScripts(this.loadAppScripts);
       pollapli.ui.loadTemplates(this.initMain);

    },
    initMain:function()
    {
       new MainRouter();
       Backbone.history.start();   
    },
    loadAppScripts:function()
    {

        //$.getScript("pollapli/routers/main_router.js",this.initMain);
    },
    success:function(data,textStatus)
    {
     console.log(data); //data returned
     console.log(textStatus); //success
     console.log('Load was performed.');
    }
};

pollapli.app=App;


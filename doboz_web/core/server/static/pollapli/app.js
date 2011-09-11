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



pollapli.ui.loadTemplates=function()
{
    var templateUrl="pollapli/templates/"
    // Using jQuery's GET method
    $.get(templateUrl+'node_templates.tpl', 
    function(doc) 
    {
        // Store a reference to the remote file's templates
        var tmpls = $(doc).filter('script');
        tmpls.each(function() 
        {
            pollapli.ui.templates[this.id] = $.jqotec(this);
        });
    });
    $.get(templateUrl+'update_templates.tpl', 
    function(doc) 
    {
        // Store a reference to the remote file's templates
        var tmpls = $(doc).filter('script');
        tmpls.each(function() 
        {
            pollapli.ui.templates[this.id] = $.jqotec(this);
           
        });
    });
    $.get(templateUrl+'event_templates.tpl', 
    function(doc) 
    {
        // Store a reference to the remote file's templates
        var tmpls = $(doc).filter('script');
        tmpls.each(function() 
        {
            pollapli.ui.templates[this.id] = $.jqotec(this);
           
        });
    });
    $.get(templateUrl+'environment_templates.tpl', 
    function(doc) 
    {
        // Store a reference to the remote file's templates
        var tmpls = $(doc).filter('script');
        tmpls.each(function() 
        {
            pollapli.ui.templates[this.id] = $.jqotec(this);
           
        });
    });
    $.get(templateUrl+'file_templates.tpl', 
    function(doc) 
    {
        // Store a reference to the remote file's templates
        var tmpls = $(doc).filter('script');
        tmpls.each(function() 
        {
            pollapli.ui.templates[this.id] = $.jqotec(this);
           
        });
    });
    $.get(templateUrl+'test.tpl', 
    function(doc) 
    {
        // Store a reference to the remote file's templates
        var tmpls = $(doc).filter('script');
        tmpls.each(function() 
        {
            pollapli.ui.templates[this.id] = $.jqotec(this);

        });
         
    });
    $.get(templateUrl+'filter_widget_templates.tpl', 
    function(doc) 
    {
        // Store a reference to the remote file's templates
        var tmpls = $(doc).filter('script');
        tmpls.each(function() 
        {
            pollapli.ui.templates[this.id] = $.jqotec(this);

        });
         
    });
     
}

pollapli.dependencies=
["pollapli/routers/pages_models.js",
"pollapli/routers/main_router.js",
]

var App = 
{
    
    Views: {},
    Routers: {},
    init: function() 
    { 
       pollapli.ui.loadTemplates();
       this.loadAppScripts();
    },
    initMain:function()
    {
       new MainRouter();
       Backbone.history.start();   
    },
    loadAppScripts:function()
    {
     
        //$.getScript("pollapli/models/pages_models.js");
        //$.getScript("pollapli/models/updates_models.js");
        //$.getScript("pollapli/views/updates_view.js");
        $.getScript("pollapli/routers/main_router.js",this.initMain);

    },
    _loadScripts:function()
    {
      
    },
    success:function(data,textStatus)
    {
     console.log(data); //data returned
     console.log(textStatus); //success
     console.log('Load was performed.');
    }
};

pollapli.app=App;


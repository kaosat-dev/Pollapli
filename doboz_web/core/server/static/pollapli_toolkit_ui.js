pollapli.ui={}
pollapli.ui.templates={};

pollapli.ui.init=function()
{

  this.showLoader();
  //load and compile all templates
  this.loadTemplates();
  
  //initialize visual elements
  //progressbars
  this.init_progressbars();

}


pollapli.ui.loadTemplates=function()
{
  
    // Using jQuery's GET method
    $.get('templates/node_templates.tpl', 
    function(doc) 
    {
        // Store a reference to the remote file's templates
        var tmpls = $(doc).filter('script');
        tmpls.each(function() 
        {
            pollapli.ui.templates[this.id] = $.jqotec(this);
        });
    });
    $.get('templates/update_templates.tpl', 
    function(doc) 
    {
        // Store a reference to the remote file's templates
        var tmpls = $(doc).filter('script');
        tmpls.each(function() 
        {
            pollapli.ui.templates[this.id] = $.jqotec(this);
           
        });
    });
    $.get('templates/event_templates.tpl', 
    function(doc) 
    {
        // Store a reference to the remote file's templates
        var tmpls = $(doc).filter('script');
        tmpls.each(function() 
        {
            pollapli.ui.templates[this.id] = $.jqotec(this);
           
        });
    });
    $.get('templates/environment_templates.tpl', 
    function(doc) 
    {
        // Store a reference to the remote file's templates
        var tmpls = $(doc).filter('script');
        tmpls.each(function() 
        {
            pollapli.ui.templates[this.id] = $.jqotec(this);
           
        });
    });
    $.get('templates/file_templates.tpl', 
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


pollapli.ui.showLoader=function()
{
    $("#loader_dialog").dialog({
    modal: true,
    draggable: false,
    resizable: false,
    autoOpen: true, 
    closeOnEscape: false,
    buttons: {},
    dialogClass: "loadingScreen",
    width:400,
    height:90
     });
}

pollapli.ui.init_nodeView=function()
{

    $( "button").button({ icons: {primary:'ui-icon-lightbulb'},text:true }); 
    $("#node-dialog").dialog({ autoOpen: false ,show:'slide',width:400})
    $("#driver-dialog").dialog({ autoOpen: false ,show:'slide',width:400})

}

pollapli.ui.openNodeDialog=function (nodeId,mode)
{
    if(nodeId!=-1)
    {
        node=manager.environments[1].nodes[nodeId];
    }
    else
    {
        node="";
    }
   
    //alert("node:"+ node+" node name:"+node.name);
    $("#node-dialog" ).dialog( "option", "title", mode+" node "  );
   // $('#node-dialog').dialog({show: 'slide' , title:" node"});
    $('#node-dialog').jqotesub(pollapli.ui.templates.nodes_dialog_tmpl, {'node':node,'mode':mode});  
    $("#node-dialog button").button();
    $('#node-dialog').dialog('open');
} 

pollapli.ui.openNodeDialog_test=function (nodeId,mode)
{
    if(nodeId!=-1)
    {
        node=manager.nodes[nodeId];
    }
    else
    {
        node="";
    }
   
    //alert("node:"+ node+" node name:"+node.name);
     $("#node-dialog" ).dialog( "option", "title", mode+" node "  );
    $('#node-dialog').jqotesub(pollapli.ui.templates.nodes_dialog_tmpl, {'node':node,'mode':mode});  
    $("#node-dialog button").button();
    
    $('#node-dialog').dialog('open');
} 


pollapli.ui.openDriverDialog=function (nodeId,mode)
{
    if(nodeId!=-1)
    {
        node=manager.nodes[nodeId];
    }
    else
    {
        node="";
    }
    $("#driver-dialog" ).dialog( "option", "title", mode+" driver "  );
    $('#driver-dialog').jqotesub(pollapli.ui.templates.driver_dialog_tmpl, {'driver':node.driver,'mode':mode});  
     $('#driverType-select').jqoteapp(pollapli.ui.templates.driverTypes_select_tmpl, manager.driverTypes);  
    
    $("#driver-dialog button").button();
    $('#driver-dialog').dialog('open');
} 



pollapli.validateNodeOp=function(op,id)
{
        var tmpnode=new Object();
        tmpnode.name=$("#nodes_dialog_name").val();
        tmpnode.description=$("#nodes_dialog_description").val();
        if (op=="create")
        {
          manager.addNodeTest(tmpnode);
        }
        else if (op=="modify")
        { 
          manager.updateNodeTest(tmpnode,id);
        }
}


pollapli.update=function(op,id)
{
 
        var tmpnode=new Object();
        tmpnode.name=$("#nodes_dialog_name").val();
        tmpnode.description=$("#nodes_dialog_description").val();

        if (op=="create")
        {
          manager.create_node(tmpnode);
        }
        else if (op=="modify")
        {
          manager.update_node(tmpnode,id);
        }
}


//calendar related methods
pollapli.ui.init_calendar=function()
{
    var date = new Date();
    var d = date.getDate();
    var m = date.getMonth();
    var y = date.getFullYear();
  
    $('#calendar').fullCalendar({
       header: {
        left: 'prev,next today',
        center: 'title',
        right: 'month,agendaWeek,agendaDay'
      },
      editable: true,
      selectable:true,
      theme: true,
      height: 650,
      dayClick: function(date, allDay, jsEvent, view) {

        if (allDay) {
            alert('Clicked on the entire day: ' + date);
        }else{
            alert('Clicked on the slot: ' + date);
        }

        alert('Coordinates: ' + jsEvent.pageX + ',' + jsEvent.pageY);

        alert('Current view: ' + view.name);

        // change the day's background color just for fun
        $(this).css('background-color', 'black');

    }
      
     });

}

//update(s) display related methods
pollapli.ui.render_update=function()
{
  
}


//
pollapli.ui.render_filesList=function()
{
  $('#fileList').jqotesub(pollapli.ui.templates.files_tmpl,null); 
  $("#_filesLi").jqotesub(pollapli.ui.templates.files_list_tmpl,manager.files); 
}

//progressbar related methods

pollapli.ui.init_progressbars=function()
{
   $('.progressbar').progressbar({value:0});
}

pollapli.ui.init_progressbar=function(divName,percent)
{
      $(divName).progressbar(
      {
         value: percent,
         change: function(event, ui) 
         {
            var newVal = $(this).progressbar('option', 'value');
            $('.pblabel', this).text(newVal + '%');
          }
        });
}

pollapli.ui.set_progressbar=function(divName,percent)
{
  $(divName).progressbar( "option", "value", percent); 
}

pollapli.ui.deleteFile=function(file)
{
  
  manager.deleteFile(file);
}


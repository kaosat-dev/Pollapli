var NodeView= Backbone.View.extend
(
  {
    initialize: function() 
    {
      this.parent=this.options.parent;
     
      this.template=this.options.template;
      if (this.template==null)
      {
        this.template=pollapli.ui.templates["nodes_tmpl"];
      }
      
      _.bindAll(this, "render","open_DeleteDialog","open_EditDialog");
      this.model.bind("all", this.render,this);    
    },
    render : function()
    {
       $(this.el).jqotesub(this.template, this.model.toJSON());
      return this;
    },
    open_DeleteDialog : function(e)
    {
       this.parent.editDialog.mode="delete";
       this.parent.editDialog.setLocal(this.model);
      // this.parent.editDialog.model=this.model;
       this.parent.editDialog.render();    
    },
    open_EditDialog : function(e)
    {
       this.parent.editDialog.mode="update";
       this.parent.editDialog.setLocal(this.model);
       //this.parent.editDialog.model=this.model;
       this.parent.editDialog.render();  
       
    },
    events :
    {
       "click a.deleteButton" : "open_DeleteDialog",
       "click a.modifyButton" : "open_EditDialog"
    },
  }
);
var NodesView= Backbone.View.extend
(
  {
    initialize: function() 
    {
     
      this.template=this.options.template;
      if (this.template==null)
      {
        this.template=pollapli.ui.templates["nodes_tmpl"];
      }
      
      this.editDialog = new NodeDialogView({el: $("#nodeDialog"),collection:this.collection}); 

      _.bindAll(this, "render","renderList");

      this.collection.bind("all", this.render,this);   
    },
    renderList : function(nodes)
    {  
      $("#innerContent").html("");
      var  self=this;
      nodes.each(function(node)
      {
        var view = new NodeView({model: node,parent:self});
        //view.parent=self;
        $("#innerContent").append(view.render().el);
      });
      return this;
    },
    render: function() 
    {
      $(this.el).html("");
      this.el.append($("<div id='innerHeader' class='widgetHeader'></div>", {id: "#innerHeader"}));
      this.el.append($("<div id='innerHeader2'> <a href='#' class='createButton ui-priority-primary ui-corner-all ui-state-default block' >Add <span class='block ui-icon ui-icon-document'></span></a></div>", {id: "#innerHeader"}));
      this.el.append($("<div id='innerContent'></div", {id: "#innerContent"}));
      this.filterView=new FilterView({el: $("#innerHeader"),orderables:["id","name"],filterables:["isConnected","isPluggedIn"] });
      this.filterView.parent=this;
      
      this.filterView.render();
      this.renderList(this.collection);
     
      return this;
    },
    add: function () 
    {
        $("#new-zone-form-dialog").dialog("open");
    },
    open_CreateDialog : function(e)
    {
        this.editDialog.mode="create";
        this.editDialog.render();
    },
    events : 
    {
        "click a.createButton" : "open_CreateDialog",
    },  
  }
);

var NodeDialogView= Backbone.View.extend
(
  {
    initialize: function() 
    {
      this.mode="create"; 
      this.template=this.options.template;
      if (this.template==null)
      {
        this.template=pollapli.ui.templates["nodes_dialog_tmpl"];
      }
      _.bindAll(this, "render","validateForm","modelSaveSucess","modelUpdateSucess","changed","setLocal");
      this.tmpModel=new Node();

      $(this.el).dialog({show: 'slide' , title:this.mode+" node",autoOpen: false,resizable:false,width:500}); 
    },
    render : function()
    { 
      $(this.el).jqotesub(this.template, {'element':this.tmpModel.toJSON(),'mode':this.mode});
      $(this.el).dialog( "option", "title", this.mode+" node");
      $(this.el).dialog('open');
      console.log("rendering node Editor mode :"+this.mode);
      return this;
    },
    setLocal : function(otherObject)
    {
      this.tmpModel=otherObject;
    },
    modelUpdateSucess : function(response)
    {
      console.log("update success");
      this.tmpModel=new Node();
    },
    modelSaveSucess : function(response)
    {
      console.log("save success");
      var tut=JSON.parse(JSON.stringify(response));
      this.tmpModel.set({"id":tut.node.id},{silent: true})
      this.collection.add( this.tmpModel.clone());
      this.tmpModel=new Node();
    },
    modelSaveError : function(response)
    {
      console.log("error");
      alert(JSON.stringify(response));
    },
    changed : function(e)
    {
       var changed = $(e.currentTarget);
       var value = changed.val();
       var obj = "{\""+changed.attr("id") +"\":\""+value+"\"}";
       var objInst = JSON.parse(obj);
       //alert("sdflksdjf"+JSON.stringify(objInst));
       this.tmpModel.set(objInst);  
    },
    validateForm : function(e)
    { 
      if(this.mode == "create")
      {
        this.tmpModel.save(null,{success: this.modelSaveSucess, error: this.modelSaveError});
      } 
      else if(this.mode=="update")
      {
         this.tmpModel.save(null,{success: this.modelUpdateSucess, error: this.modelSaveError});
      }
      else if(this.mode=="delete")
      {
        this.tmpModel.destroy();
        this.tmpModel=new Node();
      }
       $(this.el).dialog('close');
    },
    
    events :
    {
       "click .validateButton" : "validateForm",
       "change input" :"changed",
       "change select" :"changed",
       "change textarea" :"changed"
    },
  }
);
var MainRouter = Backbone.Router.extend(
{
  routes : 
  {
    "pages/:pageName" : "openInterfacePage",  
  },
  initialize:function()
  {
    this.headerView=new HeaderView({el: $("#header")});
    this.headerView.parent=this;
    
    this.pages=new Pages([]);
    
    this.nodes=new NodeCollection();
    this.nodes.fetch();
    
    this.events=new LongPollEvents();
    this.events.startLongPoll();
    
    this.updates=new Updates();
    this.updates.fetch(); 
    
    //["overview","devices","tasks","data","tools","settings","errors","updates","help"]
    
    this.pagesView = new PageView({collection: this.pages,el: $("#content")})
    this.nodesView = new NodesView({collection: this.nodes, el: $("#content") }); 
  
    this.eventsView = new EventsView({collection: this.events, el: $("#events") });
    this.eventsView.parent=this;

    this.updatesView = new UpdatesView({collection: this.updates, el: $("#content") }); 
    this.updatesView.parent=this;
    
    $("#loader_dialog").dialog('close');  
  },
  openInterfacePage : function(pageName) 
  {
   // this.document.pages.at(something).open();
    if (pageName=="updates")
    {
     // this.pagesView.remove() ;
      this.updatesView.render();   
    }
    else if(pageName=="devices")
    {
     // this.updatesView.remove() ;
      this.nodesView.render();
    }
    else
    {
      this.pagesView.render();
    }
    this.navigate("pages/" + pageName);
  },
  tutu : function()
  {
      alert("child event tutu raised and intercepted inside router")
   },
   
  
  
});
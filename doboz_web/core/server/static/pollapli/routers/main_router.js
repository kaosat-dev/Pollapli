var MainRouter = Backbone.Router.extend(
{
  routes : 
  {
    "pages/:pageName" : "openInterfacePage",  
  },
 
  initialize:function()
  {
    this.pages=new Pages([]);
    
    this.events=new LongPollEvents();
    this.eventsView = new EventsView({collection: this.events, el: $("#events") });
    
    this.updates=new Updates();
    this.updatesView = new UpdatesView({collection: this.updates, el: $("#content") }); 
    this.updates.fetch(); 
    
    this.events.startLongPoll();
    //this.filterView=new FilterView({el: $("#content"),orderables:["name","version","type"],filterables:["downloaded","installed",] });
    
  },
  openInterfacePage : function(pageName) 
  {
   // alert(pageName);
   // this.document.pages.at(something).open();
    this.navigate("pages/" + pageName);
  }
  
  
});
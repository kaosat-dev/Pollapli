var Page = Backbone.Model.extend(
{
  initialize: function()
  {        
  },
  defaults: 
  {
     name: 'DefaultPage'
  }
});
var Pages = Backbone.Collection.extend(
{
  model : Page
});
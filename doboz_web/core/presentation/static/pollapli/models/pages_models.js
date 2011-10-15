var PageManifest = Backbone.Model.extend(
{
  initialize: function()
  {        
  },
  defaults: 
  {
     contentViewRef: null
  },

});

var Page = Backbone.Model.extend(
{
  initialize: function()
  {        
  },
  defaults: 
  {
     name: 'DefaultPage',
     href: '#unassigned',
     contentView: null
  },

});

var Pages = Backbone.Collection.extend(
{
  model : Page
});
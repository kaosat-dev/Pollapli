var Driver = Backbone.Model.extend(
{
  initialize: function()
  {  
              
  },
  defaults: 
  {
    driverType : 'virtual device driver',
    isConnected : false,
    isPluggedIn : false,
    driverParams : {},
  }
});
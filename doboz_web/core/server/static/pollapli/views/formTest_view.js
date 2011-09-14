SampleView = Backbone.View.extend({
    el: '#formEl',

    events : {
        "change input" :"changed",
        "change select" :"changed"
    },

    initialize: function () {
        _.bindAll(this, "changed");
    },
    changed:function(evt) 
    {
       var changed = evt.currentTarget;
       var value = $("#"+changed.id).val();
       var obj = "{\""+changed.id +"\":\""+value+"\"}";
       var objInst = JSON.parse(obj);
       this.model.set(objInst);            
    }
 });
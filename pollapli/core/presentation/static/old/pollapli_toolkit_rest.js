pollapli.rest={}




pollapli.rest.init=function()
{
  pollapli.rest.clientId=pollapli.rest.guid();
}


////////helpers
//uuid generation
pollapli.rest.S4=function()
{
   return (((1+Math.random())*0x10000)|0).toString(16).substring(1);
}
pollapli.rest.guid= function guid() 
{
   return (S4()+S4()+"-"+S4()+"-"+S4()+"-"+S4()+"-"+S4()+S4()+S4());
}






pollapli.rest.fetchData=function(dataUrl,contentType,successCallback,errorCallback,timeout,method,data)
{
        if(!method)
          method='GET';
         if(!data)
          data='';        
          
        if(!errorCallback)
          errorCallback=this.genericErrorHandler;
        
        if (!successCallback)
        successCallback=this.genericSuccessHandler;
        
        if (!contentType)
          contentType="application/pollapli.eventList+json";
          
       if(!timeout)
          timeout=500000;
          
        $.ajax({
                    url: dataUrl+"?clientId="+this.clientId,
                    method: method,
                    async: true,
                    cache:false,
                    dataType: 'jsonp',
                    data:data,
                    contentType: contentType,
                    success: successCallback,
                    error:errorCallback,
                    complete: this.genericCompleteHandler,
                    cache:false
            });

}


pollapli.rest.postData=function(dataUrl,contentType,data,successCallback)
{  
         if(!data)
          data='';
         if (!successCallback)
        {
          successCallback=this.genericSuccessHandler;
        }
        $.ajax({
        type: 'POST',
        async:true,
        cache:false,
        dataType: 'jsonp',
        url: dataUrl+"?clientId="+this.clientId,
        data: data,
        contentType: contentType,
        success: successCallback,
        error:this.genericErrorHandler
      });
}
    
pollapli.rest.putData=function(dataUrl,contentType,data,successCallback)
{  
         if(!data)
          data='';
        if (!successCallback)
        {
          successCallback=this.genericSuccessHandler;
        }

        $.ajax({
        type: 'PUT',
        async:true,
        cache:false,
        dataType: 'jsonp',
        url: dataUrl+"?clientId="+this.clientId,
        data: data,
        contentType: contentType,
        success: successCallback,
        error:this.genericErrorHandler
      });
}
    
pollapli.rest.deleteData=function(dataUrl,contentType,data,successCallback)
{  
        if(!data)
        {
          data='';
        }
        if (!successCallback)
        {
          successCallback=this.genericSuccessHandler;
        }

        $.ajax({
        type: 'DELETE',
        async:true,
        cache:false,
        dataType: 'jsonp',
        url: dataUrl+"?clientId="+this.clientId,
        data: data,
        contentType: contentType,
        success: successCallback,
        error:this.genericErrorHandler
        
      });

}



pollapli.rest.genericCompleteHandler=function (response)
    {
        console.log("Ajax complete "+response)    ; 
    }

    
pollapli.rest.genericSuccessHandler=function (response)
{
    
        console.log("Ajax sucess "+response)    ; 
}
    
pollapli.rest.genericErrorHandler=function (response, strError)
{ console.log("Error "+strError);
      
      //errorInfo=$.parseJSON(response.responseText);
      //console.log("Error: "+errorInfo.errorCode+" msg: "+errorInfo.errorMessage+" raw: "+strError)
      //$('#errors').jqoteapp('#errors_tmpl', errorInfo);
        
       // this.errors.push(response);
       // alert("jqXHR"+request+" textStatus"+textStatus+" errorThrown"+errorThrown);
} 

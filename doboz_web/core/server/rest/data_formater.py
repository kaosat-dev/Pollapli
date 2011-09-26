import json,traceback,sys,inspect

class JsonFormater(object):
    """Class to dynamically format an object into a json representation  of itself"""
    resourceUris={"environments":"/environments","nodes":"/nodes"}
    
    
    def format(self,object,resource):
        result = {}
        if isinstance(object,list):
            result[resource] = self._formatList(object,resource)
        elif isinstance(object,dict):
            result[resource] = self._formatDict(object,resource)
        else:
            result[resource] = self._formatObject(object,resource)
        print("JSON result ",str(result))
 
        return json.dumps(result)
          
    def _formatList(self,object,resource=None):
        if resource is not None:
            singleName=resource
            pluralName=resource
            if singleName.endswith('s'):
                singleName=resource[:-1]
            else:
                pluralName=resource+'s'
        else:
            singleName=""
            pluralName=""
#        if not rootUrl.endswith('s'):
#            rootUrl=rootUrl+'s'       
        tmpDict={"link":{"href":"","rel":pluralName}}      
        tmpDict["items"]=[]
            
        def formatItem(item):
            link=tmpDict["link"]["href"]
            try:
                subElementUrlPrefix=None
                if getattr(item,"id") is not None:
                    subElementUrlPrefix=str(getattr(item,"id"))
                elif getattr(item,"name") is not None:
                    subElementUrlPrefix=getattr(item,"name")
                if subElementUrlPrefix is not None:
                    link="/"+subElementUrlPrefix
            except:pass
            
            if hasattr(item,"EXPOSE"):                    
                newItem=None
                newItem=self._formatObject(item,singleName)
                tmpDict["items"].append(newItem)   
            else:
                tmpDict["items"].append(item) 
        
        for item in object:
            formatItem(item)
        return tmpDict
                
    def _formatObject(self,object,resource=None):
        tmpDict={"link":{"href":"","rel":resource}}     
        
        if not isinstance(object,dict) and hasattr(object,"EXPOSE") :     
            for attrName in object.EXPOSE: 
                attrValue=None
                tmpattrValue=getattr(object,attrName,None)     
                if tmpattrValue is not None:
                    if attrName.startswith("_"):
                        attrName=attrName[1:]
                    if isinstance(tmpattrValue,dict):
                        tmpDict[attrName]=self._formatDict(tmpattrValue)
                    elif isinstance(tmpattrValue,list):
                        tmpDict[attrName]=self._formatList(tmpattrValue)
                    elif isinstance(tmpattrValue, (str, unicode,int,float)):
                        tmpDict[attrName]=tmpattrValue
                    else:
                        tmpDict[attrName]={"link":{"href":"/"+attrName,"rel":attrName.lower()}} 
        return  tmpDict
     
    def _formatDict(self,object,resource=None):
        tmpDict={"link":{"href":"","rel":resource}}       
        return  tmpDict

         
            
import json,traceback,sys

class DataFormater(object):
    def __init__(self,resource="resource",rootUri="http://localhost"):
        self.resource=resource
        self.rootUri=rootUri
        
    def format(self,data):  
        if self.resource.endswith('s'):
            data[self.resource]["link"]={"rel":self.resource,"href":self.rootUri}
            singleResource=self.resource[:-1]
            for item in data[self.resource]["items"]:
                if item[singleResource].get("id")is not None:
                    item[singleResource]["link"]["href"]=self.rootUri+"/"+str(item[singleResource]["id"])
                else:
                    try:
                        item[singleResource]["link"]["href"]=self.rootUri+"/"+str(item[singleResource]["name"])
                    except:pass
                #print("terf",item[singleResource]["link"])
        else:
            try:
                data[self.resource]["link"]={"rel":self.resource,"href":self.rootUri+"/"+ str(data[self.resource]["id"])}
            except:
                data[self.resource]["link"]={"rel":self.resource,"href":self.rootUri}
        return data


class DataFormater2(object):
    """new , more modular data formatter
    this should be sublcassed for each class that needs its data formated into a specific format
    @ivar resouce: The output resource type.
    @ivar rootUri: the root adress of this resource type.
    @ivar outputType: what format does this formatter render the resource to.
    @ivar ignoredAttrs: a list of attributes that will NOT be included in the final representation of this resource
    this comes into play when looping through the provide class instance's dict
    """
    def __init__(self,resource="resource",rootUri="http://localhost",outputType=None,ignoredAttrs=None,addedAttrs=None):
        self.resource=resource.lower()
        self.rootUri=rootUri
        self.outputType=outputType
        self.ignoredAttrs=ignoredAttrs
        self.addedAttrs=addedAttrs
        
    def format(self,element):
        pass
    
class JsonFormater(DataFormater2):
    """Class to dynamically format an object into a json representation  of itself"""
    def __init__(self,resource="resource",rootUri="http://localhost"):
        DataFormater2.__init__(self, resource, rootUri, "json")
        self.list=list
        self.maxRecurion=3
        self.subObjectLinksOnly=False
        
    def format(self,object,resource,rootUrl="http://localhost",maxRecursion=3,subObjectLinksOnly=True):
        return self.__format(object,resource,rootUrl,0,subObjectLinksOnly,True)
        
    def __format(self,object,resource,rootUrl="http://localhost",recursionLevel=0,subObjectLinksOnly=False,isRoot=False):
        result={}
        doIt=True
      #  print("resource",resource,"recursionLevel",recursionLevel,"maxRecurion",self.maxRecurion)  
        if recursionLevel > self.maxRecurion:  
            doIt=False
            return None
        
        if not isinstance(object,list):
            tmpDict={}      
            tmpDict["link"]={"href":rootUrl,"rel":resource} 

            if not isinstance(object,dict) and hasattr(object,"EXPOSE") and doIt:       
                for attrName in object.EXPOSE:
                    
                    attrValue=None
                    #if we are at a recusion level >0  
                            
                    if "." in attrName:
                        main,sub=attrName.split(".")
                        par=getattr(object,main)
                        attrName=sub
                        attrValue=self.__format(getattr(par,sub),attrName,tmpDict["link"]["href"]+"/"+attrName,recursionLevel+1,subObjectLinksOnly)
                    else:
                        tmpattrValue=getattr(object,attrName,None)
                  
                        
                        if tmpattrValue is not None :   
                            if not hasattr(tmpattrValue,"EXPOSE") and not isinstance(tmpattrValue,list):
                                try:
                                    json.dumps(tmpattrValue)
                                    attrValue=tmpattrValue
                                except Exception as inst:
                                    print("ERROR IN formatter",inst)
                                    attrValue=tmpattrValue.__name__
                            else:
                                try:                   
                                    attrValue=self.__format(tmpattrValue,attrName,tmpDict["link"]["href"]+"/"+attrName,recursionLevel+1,subObjectLinksOnly)
                                 
                                except Exception as inst:pass
                                    #print("Error",inst)
                                    #traceback.print_exc(file=sys.stdout)
                    if attrValue is not None:
                        tmpDict[attrName]=attrValue
                    #    print("adding ",attrName," value",attrValue,"recursionLevel",recursionLevel)
            #print("Finished adding ",tmpDict)
        else:
           
            singleName=resource
            pluralName=resource
            if resource.endswith('s'):
                singleName=resource[:-1]
            else:
                pluralName=resource+'s'
            if not rootUrl.endswith('s'):
                rootUrl=rootUrl+'s'
           
           
           # print("singleName",singleName)     
            tmpDict={}
            tmpDict["link"]={"href":rootUrl,"rel":pluralName}
            tmpDict["items"]=[]
            
            for item in object:             
                if hasattr(item,"EXPOSE"):
                    link=tmpDict["link"]["href"]
                    try:
                        subElementUrlPrefix=None
                        if getattr(item,"id") is not None:
                            subElementUrlPrefix=str(getattr(item,"id"))
                        elif getattr(item,"name") is not None:
                            subElementUrlPrefix=getattr(item,"name")
                        if subElementUrlPrefix is not None:
                            link=rootUrl+"/"+subElementUrlPrefix
                    except:pass
                  #  print("in a list, attempting to do stuff with itme",item)
                    newItem=None
                    newItem=self.__format(item,singleName,link,recursionLevel,subObjectLinksOnly)
                    tmpDict["items"].append(newItem)   

                    
                
                
        if isRoot:
            result[resource]=tmpDict  
            finalRes=None
            try:
                finalRes= json.dumps(result)
            except Exception as inst:
                print("ERROR in data formatter",inst)
            return finalRes
        else:
            return tmpDict
        
                
            
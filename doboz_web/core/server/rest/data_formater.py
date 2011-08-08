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
    def __init__(self,resource="resource",rootUri="http://localhost",ignoredAttrs=None,addedAttrs=None,list=False):
        DataFormater2.__init__(self, resource, rootUri, "json", ignoredAttrs,addedAttrs)
        self.list=list
        self.maxRecurion=4
        self.subObjectLinksOnly=False
        
    def format(self,object,resource,rootUrl="http://localhost",maxRecursion=4,subObjectLinksOnly=True):
        
        return self.__format(object,resource,rootUrl+"/"+resource,0,subObjectLinksOnly,True)
        
    def __format(self,object,resource,rootUrl="http://localhost",recursionLevel=0,subObjectLinksOnly=False,isRoot=False):
        result={}
        if not isinstance(object,list):
            tmpDict={}      
            tmpDict["link"]={"href":rootUrl,"rel":resource} 
 
            doIt=True
            if subObjectLinksOnly and recursionLevel>1:    
                doIt=False
                print("setting to False",doIt)
                         
            if doIt and not isinstance(object,dict)and hasattr(object,"EXPOSE"): 
                for attrName in object.EXPOSE:
                    attrValue=None
                    if "." in attrName:
                        main,sub=attrName.split(".")
                        par=getattr(object,main)
                        attrName=sub
                        attrValue=self.__format(getattr(par,sub),attrName,tmpDict["link"]["href"]+"/"+attrName,recursionLevel+1,subObjectLinksOnly)
                    else:
                        attrValue=getattr(object,attrName)
                        
                        if attrValue is not None :
                            try:
                                if getattr(attrValue, "EXPOSE"):
                                    attrValue=self.__format(attrValue,attrName,tmpDict["link"]["href"]+"/"+attrName,recursionLevel+1,subObjectLinksOnly)
                            except Exception as inst:pass
                                #print("Error",inst)
                                #traceback.print_exc(file=sys.stdout)
                    if attrValue is not None:
                        tmpDict[attrName]=attrValue
                        #print("attr name",attrName,"value",attrValue)
                    
                    
        else:
            singleName=resource
            pluralName=resource
            if resource.endswith('s'):
                singleName=resource[:-1]
            else:
                pluralName=resource+'s'

            if not rootUrl.endswith('s'):
                rootUrl=rootUrl+'s'
           
            tmpDict={}
            tmpDict["link"]={"href":rootUrl,"rel":pluralName}
            tmpDict["items"]=[]
            
            for item in object:
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
                print("link",link)
                
                tmpDict["items"].append(self.__format(item,singleName,link,recursionLevel+1,subObjectLinksOnly))
                
                
        if isRoot:
            result[resource]=tmpDict  
            return json.dumps(result)
        else:
            return tmpDict
            
                
    def _format(self,object,doFull=False,resource="",parentElem=None):
        result={}
        if isinstance(object,list):
            resName=resource
            singleResName=resource
            if not resName.endswith('s'):
                resName=resName+'s'
            else:
                singleResName=resource[:-1]
                
            tmpDict={}
            tmpDict["link"]={"href":self.rootUri+"/"+resName,"rel":resName}
            tmpDict["items"]=[]
            for truc in object:
                tmpDict["items"].append(self.format(truc,False,singleResName))
            if doFull:
                result[resource]=tmpDict  
                return json.dumps(result)
            else:
                return tmpDict
            
        else:
            tmpDict={}        
            for attrName in object.EXPOSE:
                attr=None
                if "." in attrName:
                    main,sub=attrName.split(".")
                    par=getattr(object,main)
                    attrName=sub
                    attr=self.format(getattr(par,sub),False,attrName)
                
                else:
                    if attrName in object.__dict__.keys():
                        attr= object.__dict__[attrName]
                        try:
                            if getattr(attr, "EXPOSE"):
                                attr=self.format(attr,False,attrName)
                        except:pass
                print("attr name",attrName,"value",attr)
                if attr is not None:
                    print("attr name",attrName,"value",attr)
                    tmpDict[attrName]=attr
                    
            if doFull:
                result[resource]=tmpDict  
                result[resource]["link"]={"href":self.rootUri+"/"+resource,"rel":resource}
                return json.dumps(result)
            else:
                return tmpDict
            
        
    def format_old(self,object):
        result={}
        
        if isinstance(object,list):
            resName=self.resource
            singleResName=self.resource
            if not resName.endswith('s'):
                resName=resName+'s'
            else:
                singleResName=self.resource[:-1]
                
                
            result[resName]={}
            result[resName]["link"]={"href":self.rootUri+"/"+resName,"rel":resName}
            result[resName]["items"]=[]
            for item in  object:
                tmpDict=item.__dict__.copy()
                if self.ignoredAttrs:
                    for ig in self.ignoredAttrs:
                        if ig in tmpDict.keys():
                            del tmpDict[ig]
                if self.addedAttrs:
                    tmpDict.update(self.addedAttrs)  
                    
                subElementUrlPrefix=None
                if tmpDict.get("id") is not None:
                    subElementUrlPrefix=str(tmpDict.get("id"))
                elif tmpDict.get("name") is not None:
                    subElementUrlPrefix=tmpDict.get("name")
                if subElementUrlPrefix is not None:
                    tmpDict["link"]={"href":self.rootUri+"/"+resName+"/"+subElementUrlPrefix,"rel":singleResName}
                result[resName]["items"].append(tmpDict)
            
        else:
            tmpDict=object.__dict__.copy()
            if self.ignoredAttrs:
                for ig in self.ignoredAttrs:
                    if ig in tmpDict.keys():
                        del tmpDict[ig]  
            if self.addedAttrs:
                tmpDict.update(self.addedAttrs)     
            result[self.resource]=tmpDict
            result[self.resource]["link"]={"href":self.rootUri+"/"+self.resource,"rel":self.resource}
        return json.dumps(result)
#        for attrName in object.__dict__:
#            if not attrName in self.ignoredAttrs:
                
            
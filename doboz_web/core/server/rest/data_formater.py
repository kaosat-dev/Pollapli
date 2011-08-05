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
        
class DataFormater(object):
    def __init__(self,resource="resource",rootUri="http://localhost"):
        self.resource=resource
        self.rootUri=rootUri
        
    def format(self,data):  
        if self.resource.endswith('s'):
            data[self.resource]["link"]={"rel":self.resource,"href":self.rootUri}
            singleResource=self.resource[:-1]
            for item in data[self.resource]["items"]:
                item[singleResource]["link"]["href"]=self.rootUri+"/"+str(item[singleResource]["id"])
                #print("terf",item[singleResource]["link"])
        else:
            data[self.resource]["link"]={"rel":self.resource,"href":self.rootUri+"/"+ str(data[self.resource]["id"])}
        return data
        
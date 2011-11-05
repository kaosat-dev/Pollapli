#TODO : clearly define what needs to be kept in memory and what needs to be persisted
#typically,only installed updates should be kept, hence some attribs are useless
class Update(object):
    """update class: for all type of updates (standard update or addon)
    Contains all needed info for handling of updates"""
    def __init__(self,type=None,name=None,description=None,version=None,downloadUrl=None,img=None,tags=None,installPath=None,downloaded=False,installed=False,enabled=False,file=None,fileHash=None,*args,**kwargs):
        self.type=type
        self.name=name
        self.description=description 
        self.version=version
        self.downloadUrl=downloadUrl
        self.img=img
        self.tags=tags
        self.file=file
        self.fileHash=fileHash
        self.downloaded=downloaded
        self.installed=installed
        self.enabled=enabled
        self.installPath=installPath
        
    def __eq__(self, other):
        return self.type == other.type and self.name == other.name and self.description == other.description and self.version == other.version 
    
    def __ne__(self, other):
        return not self.__eq__(other)
    
    def __str__(self):
        return str(self.__dict__)
    
    @classmethod
    def from_dict(self,updateDict):
        """factory method: creates an Update instance from a dict"""
        update=Update()
        for key,value in updateDict.items():
            setattr(update,key,value)  
        return update
    
    def send_signal(self,signal="",data=None):
        self.parentManager.send_signal("update_"+str(self.id)+"."+signal,data)
    
#TODO: clearly define what needs to be kept in memory and what needs to be persisted
#typically,only installed updates should be kept, hence some attribs are useless
#TODO: review equality of updates

import uuid
from pkg_resources import parse_version
from pollapli.core.logic.components.base_component import BaseComponent


class Update(BaseComponent):
    """update class: for all type of updates (standard update or addon)
    Contains all needed info for handling of updates"""
    def __init__(self,parent=None, type="update", name="Default Update", description="Default Update", version="0.0.0",downloadUrl="",img="",tags=[],installPath="",downloaded=False,installed=False,enabled=False,file=None,fileHash=None,*args,**kwargs):
        BaseComponent.__init__(self, parent)
        self.type = type
        self.name = name
        self.description = description 
        self.version = version
        self.downloadUrl = downloadUrl
        self.img = img
        self.tags = tags
        self.file = file
        self.fileHash = fileHash
        self.downloaded = downloaded
        self.installed = installed
        self.enabled = enabled
        self.installPath = installPath
        
    def __eq__(self, other):
        return self.type == other.type and self.name == other.name and self.version == other.version 
    
    def __ne__(self, other):
        return not self.__eq__(other)
    
    def __gt__(self, other):
        if self._version_cmp(self.version,other.version)>0:
            return True
        else:
            return False
    
    def __lt__(self, other):
        if self._version_cmp(self.version,other.version)<0:
            return True
        else:
            return False
    
    def __ge__(self, other):
        return self.__eq__(other) or self.__gt__(other)
    
    def __le__(self, other):
        return self.__eq__(other) or self.__lt__(other)
    
    def __str__(self):
        return str(self.__dict__)
    
    def _version_cmp(self, a, b):
        #if  mycmp(a,b)>=0 ==> a is bigger or equal to b
        #if  mycmp(a,b)<0 ==> a is lower than b
        return cmp(parse_version(a),parse_version(b))
    
    @classmethod
    def from_dict(self, updateDict):
        """factory method: creates an Update instance from a dict"""
        update = Update()
        for key,value in updateDict.items():
            if key == "id":
                update._id = uuid.UUID(value)
#            elif key == "tags":
#                update.tags = value.split(",")
            else:
                setattr(update,key,value)  
        return update
    
    def send_signal(self,signal="",data=None):
        self.parentManager.send_signal("update_"+str(self.id)+"."+signal,data)
    
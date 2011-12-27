#TODO: clearly define what needs to be kept in memory and what needs to be persisted
#typically,only installed packages should be kept, hence some attribs are useless
#TODO: review equality of packages

import uuid
from pkg_resources import parse_version
from pollapli.core.base_component import BaseComponent


class Package(BaseComponent):
    """package class: for all type of software packages (updates or addons)
    Contains all needed info on a given piece of software"""
    def __init__(self,parent=None, type="addon", name="Default Package", description="Default Package", version="0.0.0",downloadUrl="",img="",tags=[],installPath="",downloaded=False,installed=False,enabled=False,file=None,fileHash=None,targetId=None,fromVersion=None,toVersion=None,*args,**kwargs):
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

        if targetId is not None:
            self.targetId = uuid.UUID(targetId)
        self.fromVersion = fromVersion
        self.toVersion = toVersion

    def __eq__(self, other):
        if self.type == "addon":
            return self.type == other.type and self.name == other.name and self.version == other.version 
        elif self.type == "update":
            return self.type == other.type and self.name == other.name and self.targetId == other.targetId\
        and self.fromVersion == other.fromVersion and self.toVersion == other.toVersion

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
    def from_dict(self, packageDict):
        """factory method: creates an Update instance from a dict"""
        package = Package()
        for key,value in packageDict.items():
            if key == "id":
                package.cid = uuid.UUID(value)
            elif key == "targetId":
                package.targetId = uuid.UUID(value)
#            elif key == "tags":
#                package.tags = value.split(",")
            else:
                setattr(package,key,value)  
        return package

    def _send_signal(self,signal="",data=None):
        self.parentManager._send_signal("package_"+str(self.id)+"."+signal,data)
    
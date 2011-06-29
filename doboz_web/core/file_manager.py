class FileManager(object):
    rootDir=None
    
    @classmethod
    def getRootDir(cls):
        return FileManager.rootDir
    
    @classmethod
    def setRootDir(cls,rootDir):
        FileManager.rootDir=rootDir
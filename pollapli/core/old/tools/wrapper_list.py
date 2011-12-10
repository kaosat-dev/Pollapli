class WrapperList(list):
    """
    A list wrapper class with added _toDict method , for json destined
    dict
    """
    def __init__(self, data=[],rootType=""):
        list.__init__(self,data)
        self.rootType=rootType
    def _toDict(self):
        envDict={}
        envDict[self.rootType]={}
        envDict[self.rootType]["items"]=[item._toDict() for item in self]
        return envDict
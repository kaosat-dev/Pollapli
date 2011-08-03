class Vector(object):
    def __init__(self,components=[]):
        """ components is a list of chars ie ['x','y','z','e'] etc
        """
        self.components=[]
        self.componentCount=len(components)
        for component in components:
            setattr(self,component,0.0)
            
    def __iadd__(self,point):
        """need to implement addition of points/vectors"""
    
    def __isub__(self,point):
        """need to implement substraction of points/vectors"""
class Vector(object):
    def __init__(self, components=[]):
        """
        components is a list of chars ie ['x','y','z','e'] etc
        """
        self.components = []
        self.componentCount = len(components)
        for component in components:
            setattr(self, component, 0.0)

    def __iadd__(self, vector):
        """addition of points/vectors"""
        if len(self.components) != len(vector.components):
            raise Exception("Different number of components, can't add them together")
        result = Vector()
        for i in range(0, self.componentCount):
            result.components[i] = self.components[i] + vector.components[i]
        return result

    def __isub__(self, vector):
        """substraction of points/vectors"""
        if len(self.components) != len(vector.components):
            raise Exception("Different number of components, can't add them together")
        result = Vector()
        for i in range(0, self.componentCount):
            result.components[i] = self.components[i] - vector.components[i]
        return result
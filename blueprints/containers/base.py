class ContainerBase(object):
    
    def toDict(self):
       m = {}
       for key, val in self.__dict__.items():
              m[key] = val
       return m
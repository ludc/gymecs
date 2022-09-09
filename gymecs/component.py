from gymecs import dir_fields
import copy
import time

class Component:
    def __init__(self, **values):
        fields=dir_fields(self)
        for f in values:
            assert f in fields
            print(f)
            setattr(self,f,values[f])            
    
    def __str__(self):
        results=[f+"="+str(getattr(self,f)) for f in self.keys()]
        return str(type(self)) + " = " + ";".join(results)

    def structureclone(self,**args):
        c=self.__class__(id=self.id(),**{k:getattr(self,k) for k in self.keys()})
        for k,v in args.items():
            c.values[k]=v
        return c

    def deepclone(self):
        return copy.deepcopy(self)

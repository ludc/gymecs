from gymecs import dir_fields
import copy
import time

class Component:
    def __init__(self, **values):
        fields=dir_fields(self)
        for f in values:
            assert f in fields,str(f)+" // "+str(fields)
            setattr(self,f,values[f])            
    
    def __str__(self):
        results=[f+"="+str(getattr(self,f)) for f in self.keys()]
        return str(type(self)) + " = " + ";".join(results)

    def _structureclone(self,**args):
        c=self.__class__(**{k:getattr(self,k) for k in dir_fields(self)})
        for k,v in args.items():
            setattr(c,k,v)
        return c

    def _deepclone(self):
        return copy.deepcopy(self)

    def __str__(self):
        results=[]
        for f in dir_fields(self):
            results.append(f+"="+str(getattr(self,f)))
        return " ; ".join(results)

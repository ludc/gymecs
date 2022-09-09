from gymecs import dir_fields,classname_from_object

class Entity:
    def __init__(self,**components):
        fields=dir_fields(self)
        for name,c in components.items():
            assert name in fields,name+" vs "+str(fields)+" for "+str(type(self))
            setattr(self,name,c)
        
    def __str__(self):
        results=["["+classname_from_object(self)+"]"]
        for f in dir_fields(self):
            results.append("\n\t."+f+" ("+classname_from_object(getattr(self,f))+")")
            results.append(str(getattr(self,f)))
        return " ".join(results)
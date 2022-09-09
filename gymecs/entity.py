from gymecs import dir_fields

class Entity:
    def __init__(self,**components):
        fields=dir_fields(self)
        for name,c in components.items():
            assert name in fields,name+" vs "+str(fields)+" for "+str(type(self))
            setattr(self,name,c)
        
from gymecs import dir_fields,classname_from_object
from gymecs.system import LocalSystem

class World:
    def __init__(self):
        self._entities={}
    
    def set_entity(self,name,entity):
        self._entities[name]=entity
    
    def del_entity(self,name):
        del self._entities[name]
    
    def set_component(self,name,name_component,component):
        entity=self._entities[name]
        setattr(entity,name_component,component)

    def get_component(self,name,name_component):
        return getattr(self.get_entity(name),name_component)

    def get_entity(self,name):
        return self._entities[name]

    def entities_by_class(self,_class):
        for name,entity in self._entities.items():
            if isinstance(entity,_class):
                yield name,entity

    def execute(self,local_system,**arguments):
        assert isinstance(local_system,LocalSystem)
        local_system(self,**arguments)

    def keys(self):
        for name in self._entities:
            yield name

    def items(self):
        for name,entity in self._entities.items():
            yield name,entity

    def __contains__(self,key):
        return key in self._entities

    def _debug_ls(self):
        for name in self._entities:
            entity=self._entities[name]
            for f in dir_fields(entity):
                _type=classname_from_object(getattr(entity,f))
                print(name+"."+f+" : ("+str(_type)+") "+str(getattr(entity,f)))
        
    
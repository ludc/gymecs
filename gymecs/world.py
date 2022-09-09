from gymecs import dir_fields
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
        setattr(name_component,entity,component)

    def get_entity(self,name):
        return self._entities[name]

    def execute(self,local_system,**arguments):
        assert isinstance(local_system,LocalSystem)
        local_system(self,**arguments)

    def _debug_ls(self):
        for name in self._entities:
            entity=self._entities[name]
            for f in dir_fields(entity):
                _type=type(getattr(f,entity))
                print(name+"."+f+" : "+str(_type))
        
    
from gymecs import dir_fields
from gymecs.system import System

#=================== Queries
class WorldQuery:
    pass

class WorldQuery_GetEntity(WorldQuery):
    def __init__(self,name):
        self._name=name

class WorldQuery_GetComponent(WorldQuery):
    def __init__(self,name,name_component):
        self._name=name
        self._name_component=name_component

class WorldQueries(WorldQuery):
    def __init__(self,*queries):
        for q in queries: assert isinstance(q,WorldQuery)
        self._queries=queries
    
    def __iter__(self):
        for q in self._queries: yield q

#=================== Updates
class WorldUpdate:
    pass

class WorldUpdate_SetEntity(WorldUpdate):
    def __init__(self,name,entity):
        self._name=name
        self._entity=entity

class WorldUpdate_SetComponent(WorldUpdate):
    def __init__(self,name,name_component,component):
        self._name=name
        self._name_component=name_component
        self._component=component

class WorldUpdate_DelEntity(WorldUpdate):
    def __init__(self,name):
        self._name=name

class WorldUpdates(WorldUpdate):
    def __init__(self,*updates):
        for u in updates: assert isinstance(u,WorldUpdate)
        self._updates=updates

    def __iter__(self):
        for u in self._updates: yield u

 #==== WorldAPI       

class WorldAPI:
    def __init__(self):
        self._cached_updates=[]

    def set_entity(self,name,entity):
        self._cached_updates.append(WorldUpdate_SetEntity(name,entity))
    
    def del_entity(self,name):
        self._cached_updates.append(WorldUpdate_DelEntity(name))
    
    def set_component(self,name,name_component,component):
        self._cached_updates.append(WorldUpdate_SetComponent(name,name_component,component))

    def query(self,query:WorldQuery):
        raise NotImplementedError

    def get_entity(self,*name):
        query=WorldQuery_GetEntity(name)
        return self.query(query)

    def get_entities(self,*names):
        query=WorldQueries([WorldQuery_GetEntity(n) for n in names])
        return self.query(query)

    def update(self,update:WorldUpdate):
        raise NotImplementedError
    
    def flush(self):
        update=WorldUpdates(self._cached_updates)
        self._cached_updates=[]

    def execute(self,system,**arguments):
        assert isinstance(system,System)
        system(self,**arguments)

class LocalWorldAPI(WorldAPI):
    def __init__(self,world):
        super().__init__()
        self._world=world

    def query(self,query:WorldQuery):
        if isinstance(query,WorldQueries):
            return [self.query(q) for q in query]
        if isinstance(query,WorldQuery_GetEntity):
            return self._world.get_entity(query._name)
        if isinstance(query,WorldQuery_GetComponent):
            return self._world.get_component(query._name,query._name_component)

    def update(self,update:WorldUpdate):
        if isinstance(update,WorldUpdates):
            [self.update(u) for u in update]
        if isinstance(update,WorldUpdate_SetEntity):
            self._world.set_entity(update._name,update._entity)
        if isinstance(update,WorldUpdate_SetComponent):
            self._world.set_component(update._name,update._name_component,update._component)
        if isinstance(update,WorldUpdate_DelEntity):
            self._world.del_entity(update._name)
        
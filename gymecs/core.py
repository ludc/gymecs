import copy

class Component:
    def __init__(self, **values):
        for f in values:
            assert hasattr(self,f)
            setattr(self, f, values[f])

class Entity:
    def __init__(self,**components):
        for name,c in components.items():
            assert hasattr(self,name)
            setattr(self,name,c)
       
class World:
    def __init__(self):
        self._entities = {}

    def set_entity(self, name, entity):
        self._entities[name] = entity

    def del_entity(self, name):
        del self._entities[name]

    def set_component(self, name, name_component, component):
        entity = self._entities[name]
        setattr(entity, name_component, component)

    def get_component(self, name, name_component):
        return getattr(self.get_entity(name), name_component)

    def get_entity(self, name):
        return self._entities[name]

    def get_entities(self,*names):
        return [self.get_entity(name) for name in names]

    def keys(self):
        for name in self._entities:
            yield name

    def __iter__(self):
        return self.keys()

    def items(self):
        for name, entity in self._entities.items():
            yield name, entity

    def __contains__(self, key):
        return key in self._entities

class System:
    def __call__(self, world, **arguments):
        raise NotImplementedError
        
    def reset(self, seed):
        pass   

class Game:
    def reset(self, seed, **arguments)->World:
        raise NotImplementedError

    def step(self, **arguments):
        raise NotImplementedError

    def is_done(self):
        raise NotImplementedError

    def render(self, **arguments):
        pass

    
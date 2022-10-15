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

    def set_entity(self, name:str, entity:Entity):
        """ Put an entity in the world (and overwrite)

        Args:
            name (str): the name of the entity
            entity (str): the entity
        """        
        self._entities[name] = entity

    def del_entity(self, name:str):
        """ Remove an entity, assuming that it exists

        Args:
            name (str): then entity name
        """        
        del self._entities[name]

    def set_component(self, name:str, name_component:str, component:Component):
        """ Put a component (and overwrite) in the world

        Args:
            name (str): name of the entity
            name_component (str): name of the component
            component (Component): the component
        """
        entity = self._entities[name]
        setattr(entity, name_component, component)

    def get_component(self, name:str, name_component:str)->Component:
        """ Get a component

        Args:
            name (str): name of the entity
            name_component (_type_): name of the component

        Returns:
            Component: the corresponding component
        """        
        return getattr(self.get_entity(name), name_component)

    def get_entity(self, name:str)->Entity:
        """ Get an entity

        Args:
            name (str): name of the entity

        Returns:
            Entity: the corresponding entity
        """        
        return self._entities[name]

    def get_entities(self,*names)->list[Entity]:
        """ Get multiple entities

        Args:
            names (list of str): the names of the entities
        Returns:
            list[Entity]: the list of corresponding entities
        """        
        return [self.get_entity(name) for name in names]

    def keys(self):
        """ Iterator over the entities names

        Yields:
            str: name of entity
        """        
        for name in self._entities:
            yield name

    def __iter__(self):
        return self.keys()

    def items(self):
        """ Iterator over (name,Entity)

        Yields:
            tuple[str,Entity]: the tuple of name+Entity
        """        
        for name, entity in self._entities.items():
            yield name, entity

    def __contains__(self, key:str)->bool:
        """ Check if an entity exists

        Args:
            key (str): the name of the entity

        Returns:
            bool: True if the entity exists
        """        
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

    
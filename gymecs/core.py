from importlib import import_module
import numpy

def fullname_classname_from_object(o):
    klass = o.__class__
    module = klass.__module__
    if module == 'builtins':
        return klass.__qualname__ # avoid outputs like 'builtins.str'
    return module + '.' + klass.__qualname__

def fullname_classname_from_class(klass):
    module = klass.__module__
    if module == 'builtins':
        return klass.__qualname__ # avoid outputs like 'builtins.str'
    return module + '.' + klass.__qualname__

def dir_fields(c):
    return [m for m in dir(c) if not m.startswith("_")]

class Component:
    """ Describe a single component. Your own components must inherit this file
    """    
    def __init__(self,**args):
        for k,v in args.items():
            assert k in dir(self),"Field "+k+" not declared in the component."
            setattr(self,k,v)

class EntitiesIds:
    """ Describe a list of entities ids.
    """    
    def __init__(self,ids):
        self._ids=ids
        if isinstance(self._ids,list): self._ids=numpy.ndarray(self._ids)
        assert isinstance(self._ids,numpy.ndarray)
    
    def __iter__(self):
        return self._ids.__iter__()

    def __len__(self):
        return self._ids.shape[0]

    def __getitem__(self,idx):
        return self._ids[idx]


class PackedComponent:    
    """ Describe multiple components that have been packed. When _ids is not None, then each component is associated with a particular entity id.
    """
    def __init__(self,component_class,_eids=None,**arguments):
        self._component_class=component_class   
        assert isinstance(component_class(),Component),"A PackedComponent must be associated with a component class"
        self._component_classname=fullname_classname_from_class(component_class)
        for m in dir_fields(component_class):
            if m in arguments:                
                setattr(self,m,arguments[m])
            else:
                setattr(self,m,None)

    def __getitem__(self,idx):
        """ Get a particular component in the list of components. The idx is the index in the list (not the entity id)

        Args:
            idx (_type_): _description_

        Returns:
            _type_: _description_
        """        
        values={f:getattr(self,f)[idx] for f in dir_fields(self) if not getattr(self,f) is None}
        return self._component_class(**values)

class Entity:
    _id:int = None

    def __init__(self,_eid=None,**args):
        self._id=_eid
        for k,v in args.items():
            assert isinstance(v,Component),"An entity can only be composed of components"
            setattr(self,k,v)

class PackedEntity:
    _ids:EntitiesIds = None

    def __init__(self,_ids=None,**arguments):
        assert isinstance(_ids,EntitiesIds),"A PackedEntity must be built with entities ids"
        self._ids=_ids
        for m in arguments:   
                assert isinstance(arguments[m],PackedComponent),"A PackedEntity must be built using PackedComponent"
                setattr(self,m,arguments[m])

    def __len__(self):
        assert not self._ids is None
        return len(self._ids)

    def __getitem__(self,idx):
        values={f:getattr(self,f)[idx] for f in dir_fields(self) if not getattr(self,f) is None}
        eid=self._ids[idx]
        return Entity(_id=eid,**values)

class EntityStoreException(Exception):
    def __init__(self,msg):
        super().__init__(msg)


class EntityStore:
    def __init__(self,max_n_entities=100000):
        self._available_entities=[n for n in range(max_n_entities)]
        self._entities=[]
        self._entities_dict={}
        self._entities_name_dict={}

    def create_entity_id(self,name=None)->int:
        assert len(self._available_entities)>0,"Max number of entities reached"
        id=self._available_entities.pop(0)
        self._entities.append(id)
        self._entities_dict[id]=name
        if name is not None:
            assert not name in self._entities_name_dict,"Name already associated with one entity"
            self._entities_name_dict[name]=id
        return id
    
    def create_entities_ids(self,n,prefix_name=None)->EntitiesIds:
        ids=[]
        for k in range(n):
            if prefix_name is None:
                ids.append(self.create_entity_id())
            else:
                ids.append(self.create_entity_id(name=prefix_name+"/"+str(k)))
        return EntitiesIds(ids)
        
    def entity_id_exists(self,id):
        return id in self._entities_dict

    def entities_ids_exists(self,ids):
        for id in ids:
            if not self.entity_id_exists(id): return False

    def delete_entity_id(self,id):
        self._available_entities.append(id)        
        del(self._entities[self._entities.index(id)])      
        del(self._entities_dict[id])

    def delete_entities_ids(self,ids):
        for id in ids:
            self.delete_entity_id(id)

    def get_name_by_id(self,id):
        if self.has_name(id):
            return self._entities_dict[id]
        return None

    def get_id_by_name(self,name):
        assert name in self._entities_name_dict,"Name unknown '"+name+"'"
        return self._entities_name_dict[name]

    def has_name(self,id):
        return id in self._entities_dict

    def list_entities(self):
        results=[]
        for id in self._entities:
            name=None
            if self.has_name(id): name=self.get_name_by_id(id)
            results.apend((id,name))
        return results

class ComponentStore:
    def __init__(self,component_class):
        self._component_class=component_class  
        assert isinstance(component_class(),Component),"A Component store must be associated with a component class"
        
    def create_component(self,id,component:Component):
        raise NotImplementedError

    def create_components(self,ids:EntitiesIds,pcomponent:PackedComponent):
        raise NotImplementedError
 
    def update_component(self,id,component:Component):
        raise NotImplementedError

    def update_components(self,ids:EntitiesIds,pcomponent:PackedComponent):
        raise NotImplementedError

    def delete_component(self,id):
        raise NotImplementedError

    def delete_components(self,ids:EntitiesIds):
        raise NotImplementedError

class EntitiesComponentsMap:
    """ An internal class to map component class to entities (for speeding up queries)
    """    
    def __init__(self):
        self._entities_to_components={}
        self._components_to_entities={}
    
    def assign_component_to_entity(self,entity_id,component_classname):
        if not entity_id in self._entities_to_components:
            self._entities_to_components[entity_id]={}
        self._entities_to_components[entity_id][component_classname]=True

        if not component_classname in self._components_to_entities:
            self._components_to_entities[component_classname]={}
        self._components_to_entities[component_classname][entity_id]=True

    def remove_component_from_entity(self,entity_id,component_classname):
        del self._entities_to_components[entity_id][component_classname]
        del self._components_to_entities[component_classname][entity_id]
    
    def is_component_in_entity(self,entity_id,component_classname):
        return component_classname in self._entities_to_components[entity_id]

    def get_components_from_entity(self,entity_id):
        return list(self._entities_to_components[entity_id].keys())

    def get_entities_from_component(self,component_classname):
        return list(self._components_to_entities[component_classname].keys())

    def remove_entity(self,entity_id):
        c=self.get_components_from_entity(entity_id)
        del self._entities_to_components[entity_id]
        for _c in c:
            del self._components_to_entities[c][entity_id]

class WorldAPI:
    """ The interface any system will use to query a world and send new components or entities    
    """        
    def create_entity(self,entity,name=None):
        """ Create a new entity and returns its id

        Args:
            entity (Entity): The entity to add in the world
            name (str, optional): The name of the entity
        """        
        raise NotImplementedError

    def list_entities(self):
        """ Returns a list of tuples (id,name,(Components))
        """        
        raise NotImplementedError



class World(WorldAPI):
    def __init__(self):
        self._component_stores={}        
        self._entity_store=EntityStore()
        self._entities_components_map=EntitiesComponentsMap()

    def register_store(self,component_store):
        classname=fullname_classname_from_class(component_store._component_class)
        assert not classname in self._component_stores,"Component store already registered for component "+classname
        self._component_stores[classname]=component_store

    def create_entity(self,entity,name=None):
        id=self._entity_store.create_entity(name=name)        
        for f in dir_fields(entity):
            component=getattr(entity,f)
            assert isinstance(f,Component)
            classname=fullname_classname_from_object(component)
            self._component_stores[classname].create_component(id,component)
            self._entities_components_map.assign_component_to_entity(id,classname)
        return id

    def list_entities(self):
        results=[]
        for id,name in self._entity_store.list_entities():
            components=self._entities_components_map.get_components_from_entity(id)
            results.append((id,name,components))
        return results


#     def update_entities(self,pentity):
#         raise NotImplementedError

#     def assign_components(self,component_class,ids):
#         classname=component_class.__name__
#         self._component_stores[classname].create(ids)
#         for id in ids:
#             assert not classname in self._entities_to_components[id]
#             self._entities_to_components[id].append(classname)
#             self._component_to_entities[classname].append(id)

#     def delete_components(self,component_class,ids):
#         classname=component_class.__name__
#         self._component_stores[classname].delete(ids)
#         for id in ids:
#             assert classname in self._entities_to_components[id]
#             idx=self._component_to_entities[classname].index(id)
#             del(self._component_to_entities[classname][idx])
#             idx=self._entities_to_components[id].index(classname)
#             del(self._entities_to_components[id][idx])
    
#     def delete_entities(self,ids):
#         raise NotImplementedError
    
#     def update_components(self,PackedComponent):
#         raise NotImplementedError
    
#     def get_components(self,component_class,ids):
#         raise NotImplementedError

#     # def add_components(self,entity_id,*components):
#     #     for c in components:
#     #         classname=c.__class__.__name__
#     #         assert not classname in self._entities_to_components[entity_id]
#     #         self._entity_store[classname].add(c)
#     #         self._component_to_entities[classname].append(entity_id)            
#     #         self._entities_to_components[entity_id].append(classname)

#     def update_components(self,PackedComponent):
#         classname=PackedComponent._component_classname
#         store=self._component_stores[classname]
#         store.update(PackedComponent)

#     def query(self,world_query):
#         pass

#     def _monitor(self):
#         pass


 

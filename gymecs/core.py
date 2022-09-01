from importlib import import_module

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

def instantiate_class(classname,**arguments):   
    d = arguments
    module_path, class_name = classname.rsplit(".", 1)
    module = import_module(module_path)
    class_name = class_name.replace(":", ".")
    c = getattr(module, class_name)
    return c(**d)
   
class Component:
    def __init__(self,**args):
        for k,v in args.items():
            setattr(self,k,v)

class BComponent:
    _ids=None

    def __init__(self,component_class):
        self._component_class=component_class   
        self._component_classname=fullname_classname_from_class(component_class)
        for m in dir_fields(component_class):
                setattr(self,m,None)

class EntitiesStore:
    def __init__(self,max_n_entities=100000):
        self._available_entities=[n for n in range(max_n_entities)]
        self._entities=[]
        self._entities_dict={}

    def _new_entity(self)->int:
        assert len(self._available_entities)>0,"Max number of entities reached"
        id=self._available_entities.pop(0)
        self._entities.append(id)
        self._entities_dict[id]=True
        return id
    
    def create(self,n)->list[int]:
        return [self._new_entity() for _ in range(n)]

    def entity_exists(self,id):
        return id in self._entities_dict

    def entities_exists(self,ids):
        for id in ids:
            if not self.entity_exists(id): return False

    def free_entity(self,id=None):
        self._available_entities.append(id)        
        del(self._entities[self._entities.index(id)])      
        del(self._entities_dict[id])
    
class ComponentStore:
    def __init__(self,component_class):
        self._component_class=component_class   
        self._component_classname=fullname_classname_from_class(component_class)   

    def get(self,ids)->BComponent:
        raise NotImplementedError

    def update(self,bcomponent):
        raise NotImplementedError

    def create(self,ids):
        raise NotImplementedError

    def delete(self,ids):
        raise NotImplementedError

class ListComponentStore(ComponentStore):
    def __init__(self,component_class):
        super().__init__(self,component_class)
        self._components={}

    def get(self,ids)->BComponent:
        assert isinstance(ids,list) or isinstance(ids,tuple)
        bcomponent=BComponent()
        bcomponent._ids=ids
        _values={}
        for id in ids:
            c=self._values[id]
            for f in dir_fields(c):
                if not f in _values: _values[f]=[]
                _values[f].append(getattr(c,f))
        for f,v in _values.items():
            setattr(bcomponent,f,v)
        return bcomponent

    def update(self,bcomponent):
        for id in bcomponent.ids:
            component=self._component_class({k:getattr(bcomponent,k,id) for k in dir_fields(self)})
            self._components[id]=component
        
    def create(self,ids):
        for id in ids:
            self._components[id]=None

    def delete(self,ids):
        t_ids={id:1 for id in ids}
        components={k:v for k,v in self._components.items() if not k in t_ids}
        self._components=components

class World:
    def __init__(self):
        self._component_stores={}        
        self._components_to_entities={}
        self._entities_to_components={}
        
        self._entity_store=EntitiesStore()
        self._on_update={}
        self._on_delete={}
        self._on_get={}

    def register_store(self,component_store):
        classname=component_store._component_classname__
        assert not classname in self._component_stores,"Component store already registered for component "+classname
        self._component_stores[classname]=component_store
        self._components_to_entities[classname]=[]        

    def register_on_update(self,component_class,function):
        classname=component_class.__name__
        assert classname in self._component_stores
        self._on_update[component_class]=function

    def register_on_delete(self,component_class,function):
        classname=component_class.__name__
        assert classname in self._component_stores
        self._on_delete[component_class]=function

    def register_on_get(self,component_class,function):
        classname=component_class.__name__
        assert classname in self._component_stores
        self._on_get[component_class]=function

    def create_entities(self,n=1,**component_classes):
        ids=self._entity_store.create(n=n)
        for ids in id:
            self._entities_to_components[id]=[]
        
        for c in component_classes:
            classname=c.__name__
            self._entity_store[classname].create(ids)

        return ids

    def create_components(self,component_class,ids):
        classname=component_class.__name__
        self._component_stores[classname].create(ids)
        for id in ids:
            assert not classname in self._entities_to_components[id]
            self._entities_to_components[id].append(classname)
            self._component_to_entities[classname].append(id)

    def delete_components(self,component_class,ids):
        classname=component_class.__name__
        self._component_stores[classname].delete(ids)
        for id in ids:
            assert classname in self._entities_to_components[id]
            idx=self._component_to_entities[classname].index(id)
            del(self._component_to_entities[classname][idx])
            idx=self._entities_to_components[id].index(classname)
            del(self._entities_to_components[id][idx])
    
    def delete_entities(self,ids):
        raise NotImplementedError
    
    def update_components(self,bcomponent):
        raise NotImplementedError
    
    def get_components(self,component_class,ids):
        raise NotImplementedError

    # def add_components(self,entity_id,*components):
    #     for c in components:
    #         classname=c.__class__.__name__
    #         assert not classname in self._entities_to_components[entity_id]
    #         self._entity_store[classname].add(c)
    #         self._component_to_entities[classname].append(entity_id)            
    #         self._entities_to_components[entity_id].append(classname)

    def update_components(self,bcomponent):
        classname=bcomponent._component_classname
        store=self._component_stores[classname]
        store.update(bcomponent)

    def query(self,world_query):
        pass

    def _monitor(self):
        pass



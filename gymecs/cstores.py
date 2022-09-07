from gymecs.core import ComponentStore,dir_fields,BComponent,Component

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
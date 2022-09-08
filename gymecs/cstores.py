from gymecs.core import ComponentStore,dir_fields,PackedComponent,Component,EntitiesIds

class ListComponentStore(ComponentStore):
    def __init__(self,component_class):
        super().__init__(component_class)
        self._components={}

    def create_component(self,id,component:Component):
        assert not id in self._components,"id already exists in the store: "+str(id)
        assert isinstance(component,self._component_class),"the component is not off the corresponding type"
        self._components[id]=component

    def create_components(self,ids,pcomponent:PackedComponent):
        for k,id in enumerate(ids):
            self.create_component(id,pcomponent[k])
 
    def update_component(self,id,component:Component):
        assert id in self._components,"id not in the store: "+str(id)
        self._components[id]=component
       

    def update_components(self,PackedComponent:PackedComponent):
        raise NotImplementedError

    def delete_component(self,id):
        raise NotImplementedError

    def delete_components(self,ids):
        raise NotImplementedError

    # def get(self,ids)->PackedComponent:
    #     assert isinstance(ids,EntitiesIds)
    #     _values={}
    #     for id in ids:
    #         c=self._values[id]
    #         for f in dir_fields(c):
    #             if not f in _values: _values[f]=[]
    #             _values[f].append(getattr(c,f))
    #     for f,v in _values.items():
    #         setattr(bcomponent,f,v)
    #     return bcomponent

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
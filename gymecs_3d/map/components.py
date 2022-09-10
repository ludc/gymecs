from gymecs import Component,Entity
from gymecs_3d import E_PandaObject

class PandaObjectBounds(Component):
    bounds=None
    
class E_PandaMap(E_PandaObject):
    bounds:PandaObjectBounds=PandaObjectBounds()


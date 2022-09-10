from gymecs import Component,Entity
from panda3d.core import NodePath

class PandaObject(Component):
    is_in_world:bool=False
    nodepath:NodePath=None

class E_PandaObject(Entity):
    panda_object:NodePath=None

class PandaObjectPosition(Component):
    position=[0.0,0.0,0.0]

class PandaObjectForces(Component):
    impulse_force=[0.0,0.0,0.0]
    force=[0.0,0.0,0.0]

class E_PandaMovingObject(E_PandaObject):
    position:PandaObjectPosition=PandaObjectPosition()
    forces:PandaObjectForces=PandaObjectForces()









from gymecs import Component,Entity
from panda3d.core import NodePath


class BulletPhysicsTimestep(Component):
    dt:float=1.0/60
    n_steps:int = 100
    dt_step:float = 1.0/180

class E_BulletPhysics(Entity):
    step:BulletPhysicsTimestep=BulletPhysicsTimestep()

class PandaObject(Component):
    is_in_world:bool=False
    nodepath:NodePath=None

class E_PandaObject(Entity):
    panda_object:NodePath=None

class PandaObjectPosition(Component):
    position=[0.0,0.0,0.0]
    hpr=[0.0,0.0,0.0]
    linear_velocity=[0.0,0.0,0.0]

class PandaObjectForces(Component):
    impulse_force=[0.0,0.0,0.0]
    force=[0.0,0.0,0.0]

class E_PandaMovingObject(E_PandaObject):
    position:PandaObjectPosition=PandaObjectPosition()
    forces:PandaObjectForces=PandaObjectForces()

class Keyboard(Component):
    keys_pressed:dict={}

class E_Input(Entity):
    keyboard:Keyboard=Keyboard()





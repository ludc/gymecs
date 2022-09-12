from gymecs import LocalSystem,System
from gymecs_3d.components import E_BulletPhysics, E_PandaObject,E_PandaMovingObject,E_BulletPhysics,E_Input,Keyboard
from gymecs_3d.world import World3D
from panda3d.core import Vec3,Point3
from panda3d.bullet import BulletRigidBodyNode

class BulletPhysicsSystem(LocalSystem):
    def __init__(self,entity_name="bullet_step"):
        super().__init__()
        self._ename=entity_name

    def _execute(self,world,**arguments):
        if self._ename in world:
            e=world.get_entity(self._ename)
            assert isinstance(e,E_BulletPhysics)
            dt=e.step.dt
            world.get_bullet_world().doPhysics(e.step.dt,e.step.n_steps, e.step.dt_step)
            world.del_entity(self._ename)

class PandaObjectManagerSystem(LocalSystem):
    def __init__(self):
        super().__init__()

    def _execute(self,world,**arguments):
        assert isinstance(world,World3D)
        for name,entity in world.entities_by_class(E_PandaObject):
                is_in_world=entity.panda_object.is_in_world                
                if not is_in_world:
                    if world.is_np(name):    
                        if world.get_np(name).name=="bullet_body":
                            node=world.get_np(name).node()
                            world.get_bullet_world().remove(node)                            
                        for body_node in world.get_np(name).findAllMatches("**/bullet_body"):                            
                            world.get_bullet_world().remove(body_node.node())
                        world.remove_np(name)
                        world.remove_constraint(name)
                        #Remove body from bullet
                        
                    
                    entity.panda_object.nodepath.reparentTo(world.get_np())
                    if entity.panda_object.nodepath.node().name=="bullet_body":
                        world.get_bullet_world().attach(entity.panda_object.nodepath.node())
                    for body_node in entity.panda_object.nodepath.findAllMatches("**/bullet_body"):
                        world.get_bullet_world().attach(body_node.node())
                    world.set_np(name,entity.panda_object.nodepath)
                    world.set_component(name,"panda_object",entity.panda_object._structureclone(is_in_world=True))

class PandaMovingObjectSystem(LocalSystem):
    def __init__(self):
        super().__init__()

    def _execute(self,world,**arguments):
        assert isinstance(world,World3D)
        for name,entity in world.items():
            if isinstance(entity,E_PandaMovingObject):
                forces=entity.forces
                position=entity.position
                nodepath=entity.panda_object.nodepath

                #Apply forces
                body_node = world.get_np(name)  
                body_node.node().setActive(True)
                body_node.node().applyCentralForce(Vec3(*forces.force))
                body_node.node().applyImpulse(impulse=Vec3(*forces.impulse_force), pos=Point3())

                # Get position                              
                position = list(body_node.getPos())
                linearv = list(body_node.node().getLinearVelocity())
                hpr=list(body_node.getHpr())
                new_position=position._structureclone(position=position,hpr=hpr,linear_velocity=linearv)
                world.set_component(name,"position",new_position)


class InputListener(System):
    def __init__(self,input_name="input",keys=['_key_w','_key_a','_key_d','_key_s','_key_e','_key_q','_key_z','_key_x']):
        super().__init__()
        self._input_name=input_name        
        self._keys=keys

    def _execute(self,worldapi,**arguments):
        keyspressed = {}
        for k in enumerate(self._keys):                        
            if self.inputState.isSet(k):
                keyspressed[k]=1
        entity=E_Input(keyboard=Keyboard(keys_pressed=keyspressed))
        worldapi.set_entity(self._keyboard_name,entity)

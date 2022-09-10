from gymecs import LocalSystem
from gymecs_3d.components import E_PandaObject
from gymecs_3d.world import World3D


class PandaObjectManager(LocalSystem):
    def __init__(self):
        super().__init__()

    def _execute(self,world,**arguments):
        assert isinstance(world,World3D)
        for name,entity in world.items():
            if isinstance(entity,E_PandaObject):
                is_in_world=entity.panda_object.is_in_world
                if not is_in_world:
                    if world.is_np(name):                        
                        world.remove_np(name)
                        #Remove body from bullet
                        for body_node in entity.panda_object.nodepath.findAllMatches("**/bullet_body"):
                            world.get_bullet_world().remove(body_node.node())
                    
                world.set_np(entity.panda_object.nodepath)
                entity.panda_object.nodepath.reparentTo(world.get_np())
                for body_node in entity.panda_object.nodepath.findAllMatches("**/bullet_body"):
                    world.get_bullet_world().attach(body_node.node())
                
                world.set_component(name,"panda_object",entity.panda_object.structureclone(is_in_world=True))




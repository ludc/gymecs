from gymecs_3d import Asset,PandaObject
from gymecs_3d.map import E_PandaMap,PandaObjectBounds
from panda3d.core import NodePath

class Map(Asset):
    def to_entity(self,name_entity):
        _np=self.map_object.build_visual_np()
        _bnp=self.map_object.build_bullet_np()
        n=NodePath(name_entity)
        _np.reparentTo(n)
        _bnp.reparentTo(n)
        
        bounds=n.getTightBounds()
        entity=E_PandaMap(panda_object=PandaObject(is_in_world=False,nodepath=n),bounds=PandaObjectBounds(bounds=bounds))        

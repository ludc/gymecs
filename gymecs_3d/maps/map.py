from gymecs_3d import Asset,PandaObject
from gymecs_3d.maps import E_PandaMap,PandaObjectBounds
from panda3d.core import NodePath

class Map(Asset):
    def to_entity(self,name_entity,bit_mask):
        _np=self.build_visual_np()
        _bnp=self.build_bullet_np()
        n=NodePath(name_entity)
        _np.reparentTo(n)
        _bnp.reparentTo(n)
        n.setCollideMask(bit_mask) 
        bounds=n.getTightBounds()
        entity=E_PandaMap(panda_object=PandaObject(is_in_world=False,nodepath=n),bounds=PandaObjectBounds(bounds=bounds))        
        return entity

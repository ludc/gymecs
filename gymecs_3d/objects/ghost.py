from gymecs_3d import Asset,E_PandaObject,PandaObject
from panda3d.core import NodePath
from panda3d.bullet import BulletGhostNode,BulletSphereShape
from gymecs_3d.obj.loader import OBJLoader

class GhostSphere(Asset):
    def __init__(self,radius,color,obj_directory):
        if isinstance(color,str): color=eval(color)
        self._radius=radius
        self._color=color
        self._obj_directory=obj_directory
        
    def build_visual_np(self):
        loader=OBJLoader(self._obj_directory+"/_sphere.obj",(self._radius*2,self._radius*2,self._radius*2))
        vnp,_=loader.build()        
        vnp.setColor(*self._color)
        return vnp

    def build_bullet_np(self):
        node = BulletGhostNode("bullet_body")
        shape = BulletSphereShape(self._radius)
        node.addShape(shape)
        return NodePath(node)

    def to_entity(self,name_entity,bit_mask,position):
        _np=self.build_visual_np()
        _bnp=self.build_bullet_np()
        _np.reparentTo(_bnp) 
        _bnp.ls()
        n=_bnp
        _bnp.node().setActive(True)
        n.setCollideMask(bit_mask)
        n.setPos(*position)
        entity=E_PandaObject(panda_object=PandaObject(is_in_world=False,nodepath=n))        
        return entity

from gymecs_3d.maps import Map
from panda3d.core import NodePath,BitMask32,Vec3
from drain_3d.obj.tools import make_rectangle
from panda3d.bullet import BulletRigidBodyNode,BulletBoxShape

class FlatMap(Map):
    def __init__(self,size,friction,restitution,color):
        if isinstance(size,str): size=eval(size)
        if isinstance(size,int) or isinstance(size,float): size=(size,size,1.0)
        if isinstance(color,str): color=eval(color)
        self.size=size
        self.friction=friction
        self.restitution=restitution
        self.color=color
    
    def build_visual_np(self):
        sizex,sizey,sizez=self.size
        visualNP = make_rectangle(0.5 * sizex, 0.5 * sizey, 0.5 * sizez, self.color, self.color)        
        np=NodePath("flat_map")
        np.attachNewNode(visualNP)
        np.setTwoSided(True)
        return np

    def build_bullet_np(self):
        sizex,sizey,sizez=self.size
        _np = NodePath("flatmap_bullet")
        np = _np.attachNewNode(BulletRigidBodyNode("bullet_body"))
        shape = BulletBoxShape(Vec3(0.5 * sizex, 0.5 * sizey, 0.5 * sizez))
        np.node().addShape(shape)
        np.node().setMass(0.0)
        np.node().setFriction(self.friction)
        np.node().setRestitution(self.restitution)
        return np



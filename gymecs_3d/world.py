from gymecs import World
from panda3d.bullet import (BulletDebugNode, BulletGenericConstraint,BulletWorld)
from panda3d.core import NodePath

class World3D(World):
    def __init__(self,debug=True):
        super().__init__()
        self._nodepaths={"__root__":NodePath("__root__")}
        self._bullet_world= BulletWorld()
        self._debug=debug
        self._bullet_constraints={}
            
    def get_bullet_world(self):
        return self._bullet_world

    def get_np(self,key="__root__"):
        assert key in self.node_paths
        return self._nodepaths[key]

    def nps(self):
        return list(self._nodepaths.keys())

    def set_np(self,k:str,np:NodePath):
        """ Store a particular node path in the world
        """        
        assert not k in self._nodepaths
        self._nodepaths[k]=np

    def remove_np(self,k:str):
        self._nodepaths[k].removeNode()
        del(self._nodepaths[k])

    def remove_constraint(self,k:str):
        if k in self._bullet_constraints:
            self._bullet_world.remove(self._bullet_constraints[k])
            del(self._bullet_constraints[k])

    def get_constraint(self,k:str)->"BulletConstraint":
        return self._bullet_constraints[k]

    def set_constraints(self,k:str,constraint:'BulletConstraint'):
        assert not k in self._bullet_constraints
        self._bullet_constraints[k]=constraint
        self._bullet_world.attach(constraint)

    def constraints(self):
        return self._bullet_constraints.keys()

    def __del__(self): 
        for k in self.node_paths:    
            self.node_paths[k].removeNode()
        for k in self.constraints():
            self.remove_constraint(k)
           
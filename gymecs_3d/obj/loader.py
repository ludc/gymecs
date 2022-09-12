from panda3d.core import NodePath,Vec3,GeomVertexWriter,GeomVertexFormat,GeomVertexData,Geom,LMatrix4f,LVecBase3f,Material
import os
import yaml
from direct.showbase.Loader import Loader
from panda3d.bullet import BulletRigidBodyNode,BulletBoxShape,BulletTriangleMeshShape,BulletTriangleMesh
import copy
import gymecs_3d.obj

class OBJLoader:
    def __init__(self,obj_file,size):
        self.size=size        
        self.filename_obj=os.path.expanduser(obj_file)
        if not self.filename_obj in gymecs_3d.obj._objloader__loaded:
            gymecs_3d.obj._objloader__loaded[self.filename_obj]=Loader(None).loadModel(self.filename_obj,noCache=True)
        
    def build(self):        
        np=copy.deepcopy(gymecs_3d.obj._objloader__loaded[self.filename_obj])
        onp=np
        bounds=np.getTightBounds()
        x1,y1,z1=bounds[0][0],bounds[0][1],bounds[0][2]
        x2,y2,z2=bounds[1][0],bounds[1][1],bounds[1][2]
        cx,cy,cz=(x2+x1)/2.0,(y2+y1)/2.0,(z2+z1)/2.0
        real_sx,real_sy,real_sz=(x2-x1),(y2-y1),(z2-z1)
        scale_x,scale_y,scale_z=self.size[0]/real_sx,self.size[1]/real_sy,self.size[2]/real_sz        
        np.setPos(-cx,-cy,-cz)
        bounds=np.getTightBounds()
        _np=NodePath("scale")
        np.reparentTo(_np)
        np=_np
        np.setScale(scale_x,scale_y,scale_z)
        bounds=np.getTightBounds()
        np.clearModelNodes()
        #Body
        scalemat=LMatrix4f.scale_mat(LVecBase3f(scale_x,scale_y,scale_z))
        translatemat=LMatrix4f.translate_mat(LVecBase3f(-cx,-cy,-cz))
        body = BulletRigidBodyNode('bullet_body')
        body.setTag("drain_id","map")
        n_nodes=0
        for geomNP in onp.findAllMatches('**/+GeomNode'):
            n_nodes+=1
            geomNode = geomNP.node()
            ts = geomNode.getTransform()
            for geom in geomNode.getGeoms():
                geom=copy.deepcopy(geom)
                geom.transformVertices(translatemat)
                geom.transformVertices(scalemat)
                mesh = BulletTriangleMesh()
                mesh.addGeom(geom)

                
            shape = BulletTriangleMeshShape(mesh, dynamic=False)
            body.addShape(shape, ts)
        bnp=NodePath("...").attachNewNode(body)
        bnp.node().addShape(shape)
        bnp.node().setMass(0.0)
        return np,bnp

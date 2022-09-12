from gymecs import Component
from gymecs_3d import E_PandaObject,PandaObjectPosition,PandaObjectForces,PandaObject,Asset
from panda3d.core import NodePath
from gymecs import LocalSystem,System
from gymecs_3d import World3D
from panda3d.core import TransformState,Vec3,Point3,Quat
from panda3d.bullet import BulletGenericConstraint,BulletBoxShape,BulletRigidBodyNode
from gymecs_3d.obj.tools import make_cube

class BasicAgentMoveCommand(PandaObjectForces):
    turn:float=0.0
    forward:float=0.0
    jump:float=0.0

class BasicAgentState(Component):
    desired_angle:float=0.0
    on_ground:float=False
    n_seconds_since_last_jump:float=999999999999

class BasicAgentConfiguration(Component):
    forward_force:float=100.0
    rotation_speed:float=2.0
    jump_force:float=100.0
    min_seconds_between_jumps:float=1.0

class E_BasicAgent(E_PandaObject):
    position:PandaObjectPosition=PandaObjectPosition()
    command:BasicAgentMoveCommand=BasicAgentMoveCommand()
    configuration:BasicAgentConfiguration=BasicAgentConfiguration()
    state:BasicAgentState=BasicAgentState()

class BasicCubeAssetProperties(Component):
    mass:float=10.0
    scale:float=1.0
    friction:float=0.6
    restitution:float=1.0
    color:list=[1.0,0.0,0.0,1.0]
    front_color:list=[0.0,1.0,0.0,1.0]

class E_BasicCubeAgent(E_BasicAgent):
    properties:BasicCubeAssetProperties=BasicCubeAssetProperties()

class BasicAgentAsset(Asset):
    pass

class BasicCubeAsset(BasicAgentAsset):
    def __init__(self,properties,configuration):        
        if isinstance(properties.color,str): properties.color=eval(properties.color)
        if isinstance(properties.front_color,str): properties.front_color=eval(properties.front_color)        
        self._properties=BasicCubeAssetProperties(mass=properties.mass,scale=properties.scale,friction=properties.friction,restitution=properties.restitution,color=properties.color,front_color=properties.front_color)
        self._configuration=BasicAgentConfiguration(forward_force=configuration.forward_force,rotation_speed=configuration.rotation_speed,jump_force=configuration.jump_force,min_seconds_between_jumps=configuration.min_seconds_between_jumps)


    def build_visual_np(self):
        sizex,sizey,sizez=self._properties.scale,self._properties.scale,self._properties.scale,
        geom_node = make_cube(0.5 * self._properties.scale, self._properties.color, self._properties.front_color)                
        visualNP=NodePath(geom_node)
        visualNP.setTwoSided(True)
        return visualNP

    def build_bullet_np(self):
        node = BulletRigidBodyNode("bullet_body")
        shape = BulletBoxShape(Vec3(0.5 * self._properties.scale, 0.5 * self._properties.scale, 0.5 * self._properties.scale))
        node.addShape(shape)
        node.setMass(self._properties.mass)
        node.setFriction(self._properties.friction)
        node.setRestitution(self._properties.restitution)
        return NodePath(node)

    def to_entity(self,name_entity,bit_mask,position=[0.0,0.0,0.0]):
        _np=self.build_visual_np()
        _bnp=self.build_bullet_np()
        _np.reparentTo(_bnp) 
        _bnp.ls()
        n=_bnp
        # NodePath(name_entity)
        # _bnp.reparentTo(n)
        _bnp.node().setActive(True)
        n.setCollideMask(bit_mask)
        _bnp.setPos(*position)
        entity=E_BasicCubeAgent(panda_object=PandaObject(is_in_world=False,nodepath=n),position=PandaObjectPosition(),command=BasicAgentMoveCommand(),properties=self._properties._deepclone(),configuration=self._configuration._deepclone())        
        return entity

class BasicAgentMovingSystem(LocalSystem):
    def __init__(self):
        super().__init__()

    def _execute(self,world,dt,**arguments):
        assert isinstance(world,World3D)
        for name,entity in world.entities_by_class(E_BasicAgent):
                command=entity.command
                cposition=entity.position
                nodepath=entity.panda_object.nodepath

                # Get position
                body_node=nodepath
                position = list(body_node.getPos())
                linearv = list(body_node.node().getLinearVelocity())
                hpr=list(body_node.getHpr())
                new_position=cposition._structureclone(position=position,hpr=hpr,linear_velocity=linearv)
                world.set_component(name,"position",new_position)  
                
                # On ground
                on_ground=False
                result = world.get_bullet_world().contactTest(body_node.node())
                for contact in result.getContacts():            
                    on_ground = True
                if on_ground:
                    state=entity.state._structureclone(on_ground=True)
                else:
                    state=entity.state._structureclone(on_ground=False)

                #Update constraint
                if not world.is_constraint(name):                    
                    ts = TransformState.makeIdentity()
                    constraint = BulletGenericConstraint(body_node.node(), ts, True)
                    constraint.setAngularLimit(0, -0.0001, 0.0001)
                    constraint.setAngularLimit(1, -0.0001, 0.0001)
                    constraint.setAngularLimit(2, state.desired_angle - 0.0001, state.desired_angle + 0.0001)
                    constraint.setLinearLimit(0, -10000, 10000)
                    constraint.setLinearLimit(1, -10000, 10000)
                    constraint.setLinearLimit(2, -10000, 10000)        
                    world.set_constraints(name,constraint)
                
                c=world.get_constraint(name)
                c.setAngularLimit(2, state.desired_angle - 0.0001, state.desired_angle + 0.0001)

                #Apply forces
                force=[0.0,0.0,0.0]
                if command.forward!=0.0:
                    axis = Vec3(0.0, 0.0, 1.0)
                    axis.normalize()
                    quat = Quat()
                    angle=hpr[0]
                    quat.setFromAxisAngle(angle, axis)
                    vec = Vec3(0.0, -1.0, 0.0)
                    rotated_vec = quat.xform(vec)
                    force = rotated_vec * entity.configuration.forward_force * (command.forward)

                impulse_force=[0.0,0.0,0.0]
                if command.jump>0.0 and on_ground and state.n_seconds_since_last_jump>entity.configuration.min_seconds_between_jumps:
                    impulse_force=[0.0, 0.0, entity.configuration.jump_force * command.jump]
                    body_node = world.get_np(name)  
                    state=state._structureclone(n_seconds_since_last_jump=0.0)
                else:
                    state=state._structureclone(n_seconds_since_last_jump=state.n_seconds_since_last_jump+dt)              
                if command.turn!=0.0:
                    da=state.desired_angle
                    da+=command.turn*entity.configuration.rotation_speed*dt
                    state=state._structureclone(desired_angle=da)
                    
                body_node.node().setActive(True)
                body_node.node().applyCentralForce(Vec3(*force))                    
                body_node.node().applyImpulse(impulse=Vec3(*impulse_force), pos=Point3())
                world.set_component(name,"state",state)

class PandaKeyboardToCommand(System):
    from direct.showbase.InputStateGlobal import inputState

    def __init__(self,agent="agent"):
        super().__init__()
        self._agent=agent

    def _execute(self,worldapi,**arguments):
        keyspressed = {}
        forward=0.0
        jump=0.0
        turn=0.0
        if self.inputState.isSet('_key_w'):
            forward+=1.0
        if self.inputState.isSet('_key_s'):
            forward-=1.0
        if self.inputState.isSet('_key_a'):
            turn-=1.0
        if self.inputState.isSet('_key_d'):
            turn+=1.0
        if self.inputState.isSet('_key_x'):
            jump=1.0
            
        worldapi.set_component(self._agent,"command",BasicAgentMoveCommand(jump=jump,forward=forward,turn=turn))
                

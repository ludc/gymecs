from gymecs import Component,Entity,LocalSystem
from gymecs_3d.objects.ghost import GhostSphere
from gymecs_3d import E_PandaObject
import math
class Goal(Component):
    position:list=[0.0,0.0,0.0]
    radius:float=1.0

class E_Goal(E_PandaObject):
    goal:Goal=Goal()

class GoalAsset(GhostSphere):
    def __init__(self,radius,color,obj_directory):
        super().__init__(radius,color,obj_directory)
    
    def to_entity(self,name_entity,bit_mask,position):
        entity=super().to_entity(name_entity,bit_mask,position)
        gc=Goal(position=position,radius=self._radius)
        return E_Goal(panda_object=entity.panda_object,goal=gc)
    

class NavGameConfiguration(Component):
    max_episode_steps:int=1000

class NavGameState(Component):
    timestep:int=0
    timestamp:float=0.0
    done:bool=False
    interrupted:bool=False

class E_NavGame(Entity):
    state:NavGameState=NavGameState()
    configuration:NavGameConfiguration=NavGameConfiguration()

class UpdateGameState(LocalSystem):
    def __init__(self):
        super().__init__()

    def _execute(self,world,dt,**arguments):
        agent=world.get_entity("agent")
        goal=world.get_entity("goal")
        game=world.get_entity("game")
        ax,ay,az=agent.position.position
        gx,gy,gz=goal.goal.position
        distance=math.sqrt((ax-gx)**2+(ay-gy)**2+(az-gz)**2)
        done=False
        interrupted=False
        if distance<goal.goal.radius:
            done=True
        timestep=game.state.timestep
        timestep+=1
        if timestep>=game.configuration.max_episode_steps:
            interrupted=True
            done=True
        if az<-10:
            interrupted=True
            done=True
        c=NavGameState(timestep=timestep,timestamp=game.state.timestamp+dt,done=done,interrupted=interrupted)
        world.set_component('game','state',c)        

from gymecs.worldapi import LocalWorldAPI
from gymecs import Game,instantiate_class
from gymecs import System,LocalSystem
from gymecs_3d import World3D
from gymecs_3d import BulletPhysicsSystem,PandaMovingObjectSystem,PandaObjectManagerSystem,E_BulletPhysics,BulletPhysicsTimestep
from gymecs_3d.agents.basic import BasicAgentMovingSystem
import gymecs.seeding 
import math

from gymecs_examples.gymecs_nav.components import *
from gymecs_examples.gymecs_nav.gymc import *

bit_mask_agent = int(0b1011)
bit_mask_ground = int(0b0110)
bit_mask_raycast = int(0b0100)
bit_mask_goal = int(0b1000)


class NavGame(Game):
    def __init__(self,cfg):
        super().__init__()
        self._cfg=cfg
        self._systems=[]
        self.register_system(PandaObjectManagerSystem())  
        self.register_system(BulletPhysicsSystem())        
        self.register_system(BasicAgentMovingSystem())
        self.register_system(UpdateGameState())
        self._compute_gym=ComputeGym()
        self._first_reset=True
        self._world=World3D()
        
    def register_system(self,system,idx=None):
        if idx is None:
            self._systems.append(system)
        else:
            self._systems.insert(idx,system)

    def reset(self,seed,**arguments):
        self._np_random,_=gymecs.seeding.np_random(seed)
       
        self._create_map()
        self._create_goal()
        self._create_agent()
        self._create_game_state()
        
        self._worldapi=LocalWorldAPI(self._world)
        self._first_reset=False
        self._compute_gym(self._worldapi)
        return self._worldapi
    
    def step(self,_game_dt,_game_n_steps,**arguments):
        for t in range(_game_n_steps):
            bullet_step_entity=E_BulletPhysics(step=BulletPhysicsTimestep(dt=_game_dt))
            self._world.set_entity("bullet_step",bullet_step_entity)
            for s in self._systems:
                if isinstance(s,System):
                    s(self._worldapi,dt=_game_dt,**arguments)
                elif isinstance(s,LocalSystem):
                    s(self._world,dt=_game_dt,**arguments)
                else: assert False
            if self.is_done(): 
                self._compute_gym(self._worldapi)
                break        
        self._compute_gym(self._worldapi)
        
    def is_done(self):        
        return self._world.get_entity("game").state.done
    
    def _create_map(self):
        map=instantiate_class(self._cfg.map)
        entity=map.to_entity("map",bit_mask=bit_mask_ground)
        self._world.set_entity("map",entity)
    
    def _create_agent(self):
        bounds=self._world.get_entity("map").bounds.bounds
        x1,y1,z1=tuple(bounds[0])
        x2,y2,z2=tuple(bounds[1])
        x,y,z=(x2-x1),(y2-y1),(z2-z1)
        px=self._np_random.rand()*x+x1
        py=self._np_random.rand()*y+y1
        radius=self._world.get_entity("goal").goal.radius
        gx,gy,_=self._world.get_entity("goal").goal.position
        d=math.sqrt((px-gx)**2+(py-gy)**2)
        while d<radius:
            px=self._np_random.rand()*x+x1
            py=self._np_random.rand()*y+y1
            d=math.sqrt((px-gx)**2+(py-gy)**2)

        agent=instantiate_class(self._cfg.agent)
        entity=agent.to_entity("agent",bit_mask=bit_mask_agent,position=[px,py,z2+1.0])
        self._world.set_entity("agent",entity)

    def _create_goal(self):
        bounds=self._world.get_entity("map").bounds.bounds
        x1,y1,z1=tuple(bounds[0])
        x2,y2,z2=tuple(bounds[1])
        x,y,z=(x2-x1),(y2-y1),(z2-z1)
        px=self._np_random.rand()*x+x1
        py=self._np_random.rand()*y+y1

        goal=instantiate_class(self._cfg.goal)
        goal_entity=goal.to_entity("goal",bit_mask=bit_mask_agent,position=[px,py,0.0])
        self._world.set_entity("goal",goal_entity)
    
    def _create_game_state(self):
        entity=E_NavGame(configuration=NavGameConfiguration(max_episode_steps=self._cfg.max_episode_steps))
        self._world.set_entity("game",entity)
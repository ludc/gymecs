from gymecs.worldapi import LocalWorldAPI
from gymecs_examples.maze.components import *
from gymecs_examples.maze.systems import *
from gymecs import Game
from gymecs import World,System,LocalSystem

import gymecs.seeding 

class SingleMazeGame(Game):
    def __init__(self,size=(21,21),max_episode_steps=100):
        super().__init__()
        self._world=World()
        self._size=size
        self._max_episode_steps=max_episode_steps
        self._systems=[]
        self._worldapi=None

        self.register_system(MoveAgent())        
        self.register_system(UpdateGameState(max_episode_steps=self._max_episode_steps))       

    
    def register_system(self,system):
        self._systems.append(system)

    def reset(self,seed):
        self._np_random,_=gymecs.seeding.np_random(seed)

        sx,sy=self._size
        np_map=numpy.zeros(self._size)
        np_map[0,:]=1.0
        np_map[sx-1,:]=1.0
        np_map[:,0]=1.0
        np_map[:,sy-1]=1.0                
        maze=E_Maze(map=MazeMap(map=np_map),size=Size(size_x=sx,size_y=sy))                     
        self._world.set_entity("maze",maze)

        x=self._np_random.randint(sx-2)+1
        y=self._np_random.randint(sy-2)+1
        agent=E_Agent(position=Position(x=x,y=y),action=Action())
        self._world.set_entity("agent",agent)

        gx=self._np_random.randint(sx-2)+1
        gy=self._np_random.randint(sy-2)+1
        while x==gx and y==gy:
            gx=self._np_random.randint(sx-2)+1
            gy=self._np_random.randint(sy-2)+1
        goal=E_Goal(position=Position(x=gx,y=gy))
        self._world.set_entity("goal",goal)

        self._world.set_entity("game",E_GameState(state=GameState(done=False,timestep=0)))
        self._world._debug_ls()

        self._worldapi=LocalWorldAPI(self._world)
        return self._worldapi
    
    def step(self,**arguments):
        for s in self._systems:
            if isinstance(s,System):
                s(self._worldapi,**arguments)
            elif isinstance(s,LocalSystem):
                s(self._world,**arguments)
            else: assert False
        
    def is_done(self):        
        return self._world.get_entity("game").state.done


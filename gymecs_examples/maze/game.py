from gymecs_examples.maze.components import *
from gymecs import Game
from gymecs import World
import gymecs.seeding 

class SingleMazeGame(Game):
    def __init__(self,size=(21,21)):
        super().__init__()
        self._world=World()
        self._size=size
    
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
        goal=E_Goal(position=Position(x=x,y=y))
        self._world.set_entity("goal",goal)

        self._world.set_entity("game",state=GameState(done=False,timestep=1))
        self._world._debug_ls()
    
    def step(self,_game_dt,**arguments):
        pass




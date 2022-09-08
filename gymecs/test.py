from gymecs.core import Component,Entity,World,WorldAPI
from gymecs.cstores import ListComponentStore
import numpy

class Position(Component):
    x:int=0.0
    y:int=0.0

class Action(Component):
    action:int=0

class GameState(Component):
    timestep:int=0
    done:bool=False

class Maze(Component):
    maze:numpy.ndarray=None
    size:tuple=None

world=World()
world.register_store(ListComponentStore(Position))
world.register_store(ListComponentStore(Action))
world.register_store(ListComponentStore(GameState))
world.register_store(ListComponentStore(Component))

#Build maze
_maze=numpy.zeros((11,11))
_maze[0,:]=1
_maze[10,:]=1
_maze[:,0]=1
_maze[:,10]=1

maze_entity=Entity()
maze_id=world.create_entity()



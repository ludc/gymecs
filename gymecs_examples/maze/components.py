from gymecs import Component,Entity
import numpy

class Position(Component):
    x:int=0
    y:int=0

class Action(Component):
    action:int=0  

class Size(Component):
    size_x:int=0
    size_y:int=0

class MazeMap(Component):
    map:numpy.ndarray=None

class E_Agent(Entity):
    position:Position=Position()
    action:Action=Action()

class E_Goal(Entity):
    position:Position=Position()

class E_Maze(Entity):
    map:MazeMap=MazeMap()
    size:Size=Size()

class GameState(Component):
    done:bool=False
    timestep:int=0
    interrupted:bool=False

class E_GameState(Entity):
    state:GameState=GameState()

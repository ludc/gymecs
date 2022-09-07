from gymecs.core import *
import numpy

class Position(Component):
    x:int=0.0
    y:int=0.0

class Maze(Component):
    maze:numpy.ndarray=None
    size:tuple=None

position=Position(x=5,y=3)
position=Position(x=5,y=3)

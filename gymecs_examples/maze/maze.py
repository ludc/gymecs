from gymecs import Component,Entity,System,Game,World
import numpy

## Stage 1 : Components and Entities
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

class E_Maze(Entity):
    map:MazeMap=MazeMap()
    size:Size=Size()


my_agent=E_Agent(position=Position(x=5,y=3),action=Action(action=0))



##Stage  2: Systems

class MoveAgent(System):
    def __call__(self,world,**arguments):
        agent,maze=world.get_entities("agent","maze")
        mazemap=maze.map.map
        action=agent.action.action
        x,y=agent.position.x,agent.position.y
        nx,ny=x,y

        if action==0:
            nx-=1
        elif action==1:
            nx+=1
        elif action==2:
            ny-=1
        elif action==3:
            ny+=1
        if mazemap[nx,ny]==0.0:
            x=nx
            y=ny

        new_position=Position(x=x,y=y)                
        world.set_component("agent","position",new_position)

class RandomPlayer(System):
    def __init__(self):
        super().__init__()

    def __call__(self,world,**arguments):
        agent=world.get_entity("agent")
        action=numpy.random.randint(4)        
        component=Action(action=action)
        world.set_component("agent","action",component)

## Stage 3: Game

class SingleMazeGame(Game):
    def __init__(self,size=(21,21)):        
        super().__init__()
        if isinstance(size,str): size=eval(size)
        self._size=size
        self._moving_system=MoveAgent()

    def reset(self,seed):
        self._world=World()
        
        sx,sy=self._size
        np_map=numpy.zeros(self._size)
        np_map[0,:]=1.0
        np_map[sx-1,:]=1.0
        np_map[:,0]=1.0
        np_map[:,sy-1]=1.0                
        maze=E_Maze(map=MazeMap(map=np_map),size=Size(size_x=sx,size_y=sy))                     
        self._world.set_entity("maze",maze)

        x=numpy.random.randint(sx-2)+1
        y=numpy.random.randint(sy-2)+1
        agent=E_Agent(position=Position(x=x,y=y),action=Action())
        self._world.set_entity("agent",agent)
        return self._world
    
    def step(self,**arguments):
        self._moving_system(self._world,**arguments)
        
    def is_done(self):        
        return False

    def render(self):
        screen_width,screen_height=640,480
        step_x=screen_width/self._size[0]
        step_y=screen_height/self._size[0]

        try:
            import pygame
            from pygame import gfxdraw
        except ImportError:
            raise DependencyNotInstalled(
                "pygame is not installed, run `pip install gym[classic_control]`"
            )

        if not "screen" in dir(self):
            pygame.init()
            pygame.display.init()
            self.screen = pygame.display.set_mode(
                    (screen_width, screen_height)
            )
        
        self.surf = pygame.Surface((screen_width, screen_height),depth=24)
        self.surf.fill((255, 255, 255))

        mazemap=self._world.get_entity("maze").map.map
        for x in range(self._size[0]):
            for y in range(self._size[1]):
                if mazemap[x][y]==1.0:
                    x1=int(x*step_x)
                    x2=int((x+1)*step_x)
                    y1=int(y*step_y)
                    y2=int((y+1)*step_y)
                    rect = pygame.Rect(x1,y1,int(step_x)+1,int(step_y)+1)
                    gfxdraw.box(self.surf, rect, (0, 0, 0))
        
        x=self._world.get_entity("agent").position.x
        y=self._world.get_entity("agent").position.y
        x1=int(x*step_x)
        x2=int((x+1)*step_x)
        y1=int(y*step_y)
        y2=int((y+1)*step_y)
        coords = [(x1,y1), (x1, y2), (x2, y2), (x2, y1)]
        gfxdraw.filled_polygon(self.surf, coords, (255 ,0 , 0))

        self.screen.blit(self.surf, (0, 0))
        pygame.display.flip()
        
if __name__=="__main__":
    game=SingleMazeGame((21,21))
    player=RandomPlayer()

    world=game.reset(0)
    player.reset(0)
    player(world)
    while not game.is_done():
        game.step()
        player(world)
        game.render()
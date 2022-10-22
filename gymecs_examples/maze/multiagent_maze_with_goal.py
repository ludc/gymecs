from gymecs import Component,Entity,System,Game,World
import numpy
import time

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

class AgentState(Component):
    collide_wall:bool=False
    collide_with:str=None
    on_goal:bool=False

class E_Agent(Entity):
    position:Position=Position()
    action:Action=Action()
    state:AgentState=AgentState()

class E_Maze(Entity):
    map:MazeMap=MazeMap()
    size:Size=Size()

class E_Goal(Entity):
    position:Position=Position()

class GameInfos(Component):
    timestep:int=0
    winner:str=None

class E_GameState(Entity):
    infos:GameInfos()=GameInfos()

##Stage  2: Systems

class MoveAgent(System):
    def __call__(self,world,**arguments):
        maze,goal=world.get_entities("maze","goal")

        #Build a list of agent positions
        agent_positions={}
        for name_agent,agent in world.get_entities_by_type(E_Agent):
            x,y=agent.position.x,agent.position.y
            agent_positions[(x,y)]=name_agent

        #Loop for all agents
        for name_agent,agent in world.get_entities_by_type(E_Agent):
            state=agent.state
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
                state=state._structureclone(collide_wall=False)
                if (nx,ny) in agent_positions:
                    state._structureclone(collide_with=agent_positions[(nx,ny)])
                else:
                    state._structureclone(collide_with=None)
                    x=nx
                    y=ny
                    if goal.position.x==x and goal.position.y==y:
                        state=state._structureclone(on_goal=True)
                    else:
                        state=state._structureclone(on_goal=False)
            else:
                state=state._structureclone(collide_wall=True,collide_with=None)

            position=Position(x=x,y=y)                
            world.set_component(name_agent,"position",position)
            world.set_component(name_agent,"state",state)

class UpdateGameState(System):
    def __call__(self,world,**arguments):
        game=world.get_entity("game")
        infos=game.infos
        
        winner=None
        for name_agent,agent in world.get_entities_by_type(E_Agent):
            if agent.state.on_goal:
                winner=name_agent
        
        infos=infos._structureclone(timestep=infos.timestep+1,winner=winner)
        world.set_component("game","infos",infos)


class RandomPlayer(System):
    def __init__(self,name):
        super().__init__()
        self._name=name

    def __call__(self,world,**arguments):
        agent=world.get_entity(self._name)
        action=numpy.random.randint(4)        
        component=Action(action=action)
        world.set_component(self._name,"action",component)

## Stage 3: Game

class MultiAgentMazeGame(Game):
    def __init__(self,size=(21,21),wall_density=0.1,n_agents=4):        
        super().__init__()
        if isinstance(size,str): size=eval(size)
        self._size=size
        self._n_agents=n_agents
        self._wall_density=wall_density
        self._moving_system=MoveAgent()
        self._update_game_system=UpdateGameState()
        self._players=[]

    def add_player(self,system):
        self._players.append(system)

    def _generate_map(self):
        sx,sy=self._size
        np_map=numpy.zeros(self._size)
        np_map[0,:]=1.0
        np_map[sx-1,:]=1.0
        np_map[:,0]=1.0
        np_map[:,sy-1]=1.0                

        for x in range(1,sx-1):
            for y in range(1,sy-1):
                if numpy.random.rand()<self._wall_density:
                    np_map[x,y]=1.0

        return E_Maze(map=MazeMap(map=np_map),size=Size(size_x=sx,size_y=sy))                     

    def _generate_agent(self):
        maze,goal=self._world.get_entities("maze","goal")
        sx,sy=self._size
        gx,gy=goal.position.x,goal.position.y
        
        #Build a list of agent positions
        agent_positions={}
        for name_agent,agent in self._world.get_entities_by_type(E_Agent):
            x,y=agent.position.x,agent.position.y
            agent_positions[(x,y)]=name_agent


        x=numpy.random.randint(sx-2)+1
        y=numpy.random.randint(sy-2)+1
        while maze.map.map[x,y]==1.0 or (gx==x and gy==y) or ((x,y) in agent_positions):
            x=numpy.random.randint(sx-2)+1
            y=numpy.random.randint(sy-2)+1
        
        return E_Agent(position=Position(x=x,y=y),action=Action())

    def _generate_goal(self):
        maze=self._world.get_entity("maze")
        sx,sy=self._size

        x=numpy.random.randint(sx-2)+1
        y=numpy.random.randint(sy-2)+1
        while (maze.map.map[x,y]==1.0):
            x=numpy.random.randint(sx-2)+1
            y=numpy.random.randint(sy-2)+1
        
        return E_Goal(position=Position(x=x,y=y))


    def reset(self,seed):
        self._world=World()
        
        maze=self._generate_map()
        self._world.set_entity("maze",maze)

        goal=self._generate_goal()
        self._world.set_entity("goal",goal)

        for k in range(self._n_agents):
            agent=self._generate_agent()
            self._world.set_entity("agent#"+str(k),agent)
        
        game=E_GameState()
        self._world.set_entity("game",game)
        
        for p in self._players:
            p(self._world)

        return self._world
    
    def step(self,**arguments):
        self._moving_system(self._world,**arguments)
        self._update_game_system(self._world,**arguments)
        for p in self._players:
            p(self._world)
        
    def is_done(self):        
        return not self._world.get_entity("game").infos.winner is None

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
        
        for name_agent,agent in self._world.get_entities_by_type(E_Agent):
            k=int(name_agent[-1])
            x=agent.position.x
            y=agent.position.y
            x1=int(x*step_x)
            x2=int((x+1)*step_x)
            y1=int(y*step_y)
            y2=int((y+1)*step_y)
            coords = [(x1,y1), (x1, y2), (x2, y2), (x2, y1)]
            gfxdraw.filled_polygon(self.surf, coords, (64+int(180/self._n_agents)*k ,0 , 0))

        x=self._world.get_entity("goal").position.x
        y=self._world.get_entity("goal").position.y
        x1=int(x*step_x)
        x2=int((x+1)*step_x)
        y1=int(y*step_y)
        y2=int((y+1)*step_y)
        coords = [(x1,y1), (x1, y2), (x2, y2), (x2, y1)]
        gfxdraw.filled_polygon(self.surf, coords, (0 ,255 , 0))

        self.screen.blit(self.surf, (0, 0))
        pygame.display.flip()
        
if __name__=="__main__":
    n_agents=4
    game=MultiAgentMazeGame((21,21),wall_density=0.05,n_agents=n_agents)
    players=[RandomPlayer("agent#"+str(k)) for k in range(n_agents)]

    world=game.reset(0)
    [player.reset(0) for player in players]
    [player(world) for player in players]
    while not game.is_done():
        game.step()
        [player(world) for player in players]
        game.render()
    print("End at timestep ",world.get_entity("game").infos.timestep)
    print("Winner is ",world.get_entity("game").infos.winner)
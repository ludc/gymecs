from gymecs import System


class MoveAgent(System):
    def _execute(self,worldapi,**arguments):
        agent,maze=worldapi.get_entities("agent","maze")
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
        if mazemap[x,y]==0.0:
            x=nx
            y=ny
        new_position=agent.position._structureclone(x=x,y=y)
        worldapi.set_component("agent","position",new_position)
        
class UpdateGameState(System):
    def __init__(self,max_episode_steps):
        self._max_episode_steps=max_episode_steps

    def _execute(self,worldapi,**arguments):
        agent,goal,game=worldapi.get_entities("agent","goal","game")        
        x,y=agent.position.x,agent.position.y
        gx,gy=goal.position.x,agent.position.y
        timestep=game.state.timestep
        timestep+=1
        interrupted=timestep>=self._max_episode_steps
        done=(x==gx and y==gy) or interrupted
        new_state=game.state._structureclone(done=done,interrupted=interrupted,timestep=timestep)
        print(new_state)
        worldapi.set_component("game","state",new_state)





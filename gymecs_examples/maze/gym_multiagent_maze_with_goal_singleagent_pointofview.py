from gymecs import Component,Entity,System,Game,World
from gymecs.togym import GymEnv
from gymecs_examples.maze.maze import RandomPlayer
from gymecs_examples.maze.multiagent_maze_with_goal import MultiAgentMazeGame,Action,RandomPlayer
import numpy

class SingleAgentPointOfView(GymEnv):
    """ A game as a gym environnement focused on one particular agent

    """    
    def __init__(self,game,idx_agent):
        super().__init__(game=game)
        self._idx_agent=idx_agent

    def _get_observation(self):
        agent=self._world.get_entity("agent#"+str(self._idx_agent))
        return [agent.position.x,agent.position.y]

    def _get_reward(self):
        agent=self._world.get_entity("agent#"+str(self._idx_agent))
        if agent.state.collide_wall: return -0.1
        if agent.state.on_goal: return 10.0
        if not agent.state.collide_with is None: return -0.5
        return -1.0

    def _get_done(self):
        agent=self._world.get_entity("agent#"+str(self._idx_agent))
        return agent.state.on_goal

    def _update_with_action(self, action):
        self._world.set_component("agent#"+str(self._idx_agent),"action",Action(action=action))        
       

if __name__=="__main__":
    idx_agent=0
    n_agents=4
    game=MultiAgentMazeGame(size=(21,21),wall_density=0.01,n_agents=4)
    
    for i in range(n_agents):
        if not i==idx_agent:
            game.add_player(RandomPlayer("agent#"+str(i)))
    
    gymenv=SingleAgentPointOfView(game,idx_agent)
    gymenv.seed(0)
    gymenv.reset()
    gymenv.render()
    while True:
        action=numpy.random.randint(4)
        observation,reward,done,_=gymenv.step(action)
        print(observation,reward,done)
        gymenv.render()
        if done: break



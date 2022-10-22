from gymecs import Component,Entity,System,Game,World
from gymecs.togym import GymEnv
from gymecs_examples.maze.maze import RandomPlayer
from gymecs_examples.maze.multiagent_maze_with_goal import MultiAgentMazeGame,Action,RandomPlayer,E_Agent
import numpy

class AllAgentsPointOfView(GymEnv):
    """ A game as a gym environnement focused on all the agents

    """    
    def __init__(self,game):
        super().__init__(game=game)

    def _get_observation(self):
        results={}
        for name_agent,agent in self._world.get_entities_by_type(E_Agent):
            results[name_agent]=[agent.position.x,agent.position.y]
        return results

    def _get_single_reward(self,idx_agent):
        agent=self._world.get_entity("agent#"+str(idx_agent))
        if agent.state.collide_wall: return -0.1
        if agent.state.on_goal: return 10.0
        if not agent.state.collide_with is None: return -0.5
        return -1.0

    def _get_reward(self):
        return sum([self._get_single_reward(k) for k in range(self._game._n_agents)])

    def _get_done(self):
        for name_agent,agent in self._world.get_entities_by_type(E_Agent):
            if agent.state.on_goal: return True
        return False

    def _update_with_action(self, action):
        for k in range(self._game._n_agents):
            self._world.set_component("agent#"+str(k),"action",Action(action=action[k]))        
       
if __name__=="__main__":
    n_agents=4
    game=MultiAgentMazeGame(size=(21,21),wall_density=0.01,n_agents=4)

    
    gymenv=AllAgentsPointOfView(game)
    gymenv.seed(0)
    gymenv.reset()
    gymenv.render()
    while True:
        action=[numpy.random.randint(4) for _ in range(n_agents)]
        observation,reward,done,_=gymenv.step(action)
        print(observation,reward,done)
        gymenv.render()
        if done: break



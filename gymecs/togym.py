import gym
from gymecs.core import Game
import numpy

class GymEnv(gym.Env):
    def _get_observation(self):
        raise NotImplementedError

    def _get_reward(self):
        raise NotImplementedError

    def _get_done(self):
        raise NotImplemented

    def _update_with_action(self, action):
        raise NotImplementedError

    def __init__(self, game:Game):
        super().__init__()
        self._game = game
        self._seed = None
        self._world = None

    def reset(self):
        assert not self._seed is None
        self._world = self._game.reset(self._seed)
        return self._get_observation()

    def step(self, action):
        self._update_with_action(action)
        self._game.step()
        reward = self._get_reward()
        done = self._get_done()
        obs = self._get_observation()
        return obs, reward, done, {}

    def seed(self, seed):
        self._seed = seed

    def render(self, **arguments):
        self._game.render(**arguments)

if __name__=="__main__":
    from gymecs_examples.maze.maze import SingleMazeGame,Action

    class MazeGymEnv(GymEnv):
        def __init__(self,size=(21,21)):
            super().__init__(game=SingleMazeGame(size))

        def _get_observation(self):
            agent=self._world.get_entity("agent")
            return [agent.position.x,agent.position.y]

        def _get_reward(self):
            return -1.0

        def _get_done(self):
            return False

        def _update_with_action(self, action):
            self._world.set_component("agent","action",Action(action=action))        
    
    gymenv=MazeGymEnv()
    gymenv.seed(0)
    gymenv.reset()
    gymenv.render()
    while True:
        action=numpy.random.randint(4)
        observation,reward,done,_=gymenv.step(action)
        gymenv.render()
        if done: break

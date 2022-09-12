import gym
from gymecs import AutoResetGame
import numpy as np

class GymEnv(gym.Env):
    def __init__(self,game,step_arguments={}):
        super().__init__()
        self._game=game
        self._seed=None
        self._worldapi=None
        self._step_arguments=step_arguments



    def _get_observation(self):
        raise NotImplementedError

    def _get_reward(self):
        raise NotImplementedError

    def _get_done(self):
        raise NotImplemented

    def reset(self):
        assert not self._seed is None
        self._worldapi=self._game.reset(self._seed)
        return self._get_observation()

    def _update_with_action(self,action):
        raise NotImplementedError

    def step(self,action):
        self._update_with_action(action)
        self._game.step(**self._step_arguments)
        reward=self._get_reward()
        done=self._get_done()
        obs=self._get_observation()
        return obs,reward,done,{}

    def seed(self,seed):
        self._seed=seed

    def render(self,**arguments):
        raise NotImplementedError

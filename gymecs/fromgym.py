import gym
from gymecs.core import Game,Component,Entity,World,System
import numpy

class AgentObservation(Component):
    env_obs = None
    reward: float = None

class AgentAction(Component):
    action = None

class E_Agent(Entity):
    observation: AgentObservation = AgentObservation()
    action: AgentAction = AgentAction()
    
class GameState(Component):
    done: bool = False
    timestep: int = 0

class GameEnv(Component):
    gym_env: gym.Env = None

class Game(Entity):
    state: GameState = GameState()
    env: GameEnv = GameEnv()


class Step(System):
    def __call__(self,world,**arguments):
        agent = world.get_entity("agent")
        game=world.get_entity("game")
        action = agent.action.action
        obs, reward, done, _ = game.env.gym_env.step(action)
        entity = E_Agent(
                observation=AgentObservation(env_obs=obs, reward=reward),                
        )
        world.set_entity("agent", entity)
        world.set_component("game", "state",GameState(done=done,timestep=game.state.timestep+1))

class GameFromGym(Game):
    def __init__(self, env_name,env_arguments={}):
        self._env_name=env_name
        self._env_arguments=env_arguments
        self._system=Step()

    def reset(self, seed, **arguments):
        env= gym.make(self._env_name,**self._env_arguments)        
        env.seed(seed)
        
        self._world = World()        
        obs = env.reset()
        entity = E_Agent(observation=AgentObservation(env_obs=obs))
        self._world.set_entity("agent", entity)
        self._world.set_entity("game", Game(state=GameState(done=False),env=GameEnv(gym_env=env)))
        return self._world

    def step(self, **arguments):
        self._system(self._world,**arguments)

    def is_done(self):
        return self._world.get_component("game", "state").done

    def render(self, **kargs):
        self._world.get_entity("game").env.gym_env.render(**kargs)

class RandomMountainCarPlayer(System):
    def __call__(self,world,**arguments):
        action=numpy.random.randint(2)
        world.set_component("agent","action",AgentAction(action=action))
    
    def reset(self,seed):
        pass

if __name__=="__main__":
    game=GameFromGym("CartPole-v0")
    world=game.reset(0)
    player=RandomMountainCarPlayer()
    player.reset(0)
    player(world)
    game.render()
    while not game.is_done():
        game.step()
        if not game.is_done(): player(world)
        game.render()
    print("End at timestep = ",world.get_entity("game").state.timestep)

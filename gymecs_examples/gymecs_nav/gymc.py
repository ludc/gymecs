from gymecs import Component,Entity,System,AutoResetGame,instantiate_class,dir_fields
from gymecs_3d import GymEnv3D
from gymecs_3d.agents import BasicAgentMoveCommand
import math
import hydra
import numpy as np

class GymObservation(Component):
    position:list=[0.0,0.0,0.0]
    normalized_position=[0.0,0.0,0.0]
    goal_position:list=[0.0,0.0,0.0]
    goal_normalized_position=[0.0,0.0,0.0]
    goal_relative_position:list=[0.0,0.0,0.0]
    goal_relative_normalized_position=[0.0,0.0,0.0]
    angle:float=0.0
    speed:float=0.0
    env_obs:list=None

class GymInfos(Component):
    done:bool=False
    interrupted:bool=False
    reward:float=0.0

class E_Gym(Entity):
    observation:GymObservation=GymObservation()
    infos:GymInfos=GymInfos()

class ComputeGym(System):
    def __init__(self):
        super().__init__()

    def _execute(self,worldapi,**arguments):
        agent,goal,map,game=worldapi.get_entities("agent","goal","map","game")
        bounds=map.bounds.bounds
        x1,y1,z1=bounds[0]
        x2,y2,z2=bounds[1]
        position=agent.position.position
        gposition=goal.goal.position
        nposition=(position[0]-x1)/(x2-x1)*2.0-1.0,(position[1]-y1)/(y2-y1)*2.0-1.0,(position[2]-z1)/(z2-z1)*2.0-1.0
        ngposition=(gposition[0]-x1)/(x2-x1)*2.0-1.0,(gposition[1]-y1)/(y2-y1)*2.0-1.0,(gposition[2]-z1)/(z2-z1)*2.0-1.0
        relative_position=position[0]-gposition[0],position[1]-gposition[1],position[2]-gposition[2]
        n_relative_position=nposition[0]-ngposition[0],nposition[1]-ngposition[1],nposition[2]-ngposition[2]
        
        vx,vy,vz=agent.position.linear_velocity
        speed=math.sqrt(vx**2+vy**2+vz**2)
        
        angle=agent.position.hpr[0]
        while angle>180: angle-=360
        while angle<-180: angle+=360
        angle=math.radians(angle)
        
        observation=n_relative_position+(speed,)+(angle,)

        c_observation=GymObservation(
            position=list(position),
            normalized_position=list(nposition),
            goal_position=list(gposition),
            goal_normalized_position=list(ngposition),
            goal_relative_position=list(relative_position),
            goal_relative_normalized_position=list(n_relative_position),
            speed=speed,
            angle=angle,
            env_obs=list(observation)
        )

        ## Infos
        done=game.state.done
        interrupted=game.state.interrupted
        reward=-1.0
        c_infos=GymInfos(done=done,interrupted=interrupted,reward=reward)
        worldapi.set_entity("gym",E_Gym(observation=c_observation,infos=c_infos))

class NavGameGym(GymEnv3D):
    def __init__(self,navgame,_game_dt=1.0/30.0,_game_n_steps=1):
        super().__init__(game=navgame,step_arguments={"_game_dt":_game_dt,"_game_n_steps":_game_n_steps})

    def _get_observation(self):
        observation=self._worldapi.get_component("gym","observation")
        observation={k:getattr(observation,k) for k in dir_fields(observation)}    
        return observation

    def _get_reward(self):
        return self._worldapi.get_component("gym","infos").reward

    def _get_done(self):
        return self._worldapi.get_component("gym","infos").done

    def _update_with_action(self,action):
        component=BasicAgentMoveCommand(forward=action[0],turn=action[1],jump=action[2])
        self._worldapi.set_component("agent","command",component)


@hydra.main(config_path="./yaml", config_name="run.yaml")
def main(cfg):
    game = instantiate_class(cfg.game)
    player = instantiate_class(cfg.player)    
    game=AutoResetGame(game)
    gymenv=NavGameGym(game)
    gymenv.seed(0)
    print(gymenv.reset())
    while True:
        action=[np.random.rand()*2.0-1.0,np.random.rand()*2.0-1.0,np.random.rand()*2.0-1.0]
        #action=[1.0,0.0,0.0]
        obs,reward,done,_=gymenv.step(action)
        gymenv.render()
        print(obs,reward,done)

if __name__ == "__main__":
    main()    

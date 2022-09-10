import hydra
import sys

import numpy as np
from direct.showbase.InputStateGlobal import inputState
from direct.showbase.ShowBase import ShowBase
from drain.cast import cast_to_numpy
from panda3d.bullet import BulletDebugNode, BulletWorld
from panda3d.core import (AmbientLight, BitMask32, ClockObject,
                          DirectionalLight, Vec3, Vec4, Quat,PointLight)
from panda3d.core import loadPrcFileData

loadPrcFileData('','win-size 1024 768')

class PandaShowBase(ShowBase):
    def __init__(
        self,
        game,
        player,
        use_multigame,
        player_args,
        keyboard_to_event,
        _game_dt,
        _game_n_steps,
        view_all_steps,
        first_person
    ):
        super().__init__()
        self.first_person=first_person
        self.use_multigame=use_multigame
        self.game = game
        self.player = player
        self.keyboard_to_event = keyboard_to_event
        self._game_dt = _game_dt
        self._game_n_steps = _game_n_steps
        self.view_all_steps = view_all_steps
        self.timestep = 0
        self.player_args = player_args

        base.setBackgroundColor(0.1, 0.1, 0.1, 1)
        base.setFrameRateMeter(True)

        
        base.cam.setPos(0, -60, 4)
        base.cam.lookAt(5, 0, 0)

        # Create Ambient Light
        ambientLight = AmbientLight('ambientLight')
        ambientLight.setColor((0.8, 0.8, 0.8, 1))
        ambientLightNP = render.attachNewNode(ambientLight)
        render.setLight(ambientLightNP)

        # Directional light 01
        directionalLight = DirectionalLight('directionalLight')
        directionalLight.setColor((0.8, 0.8, 0.8, 1))
        directionalLightNP = render.attachNewNode(directionalLight)
        # This light is facing backwards, towards the camera.
        directionalLightNP.setHpr(180, -20, 0)
        render.setLight(directionalLightNP)

        # # Directional light 02
        # directionalLight = DirectionalLight('directionalLight')
        # directionalLight.setColor((0.2, 0.2, 0.8, 1))
        # directionalLightNP = render.attachNewNode(directionalLight)
        # # This light is facing forwards, away from the camera.
        # directionalLightNP.setHpr(0, -20, 0)
        # render.setLight(directionalLightNP)
        
        self.accept("escape", self.doExit)

        for key, event in keyboard_to_event.items():
            print(event, key)
            inputState.watchWithModifiers(event, key)

        # Task
        taskMgr.add(self.update, "updateWorld")
        self.inputState = inputState
        globalClock.setMode(ClockObject.MLimited)
        fps = int(1.0 / self._game_dt)
        print(".. Setting FPS to ", fps)
        globalClock.setFrameRate(fps)

    # _____HANDLER_____

    def doExit(self):
        self.cleanup()
        sys.exit(1)

    def update(self, task):
        gnp=None
        if self.use_multigame:
            gnp=self._game.games[0].game.world.get_manager("scene_graph").get_np()
        else:
            gnp=self._game.world.get_manager("scene_graph").get_np()
        if self._node_path!=gnp:
            if not self._node_path is None: self._node_path.removeNode()
            self._node_path=gnp
            self._node_path.reparentTo(render)

        dt = globalClock.getDt()
        if self.view_all_steps:
            self.game.step(_game_dt=self._game_dt, _game_n_steps=1)

            self.player(self.worldapi, **self.player_args)         
        else:
            self.game.step(_game_dt=self._game_dt, _game_n_steps=self._game_n_steps)
            self.player(self.worldapi, **self.player_args)
        component=self.worldapi.query_set("agent")["agent"]
        
        if self.first_person:
            cpos=component["position"]
            cpos=Vec3(*cpos)
            cangle=component["angle"]
            axis = Vec3(0.0, 0.0, -1.0)
            axis.normalize()
            quat = Quat()
            quat.setFromAxisAngle(cangle, axis)
            vec = Vec3(0.0, -5.0, 0.0)
            rotated_vec = quat.xform(vec)
            vec = Vec3(0.0, -1.0, 0.0)
            rotated_vec = quat.xform(vec)
            cam_pos=cpos-rotated_vec
            cam_pos[2]+=1.0
            base.cam.setPos(cam_pos)
            vec = Vec3(0.0, -15.0, 0.0)
            rotated_vec = quat.xform(vec)
            base.cam.lookAt(*(cpos+rotated_vec))

        self.timestep += 1
        return task.cont

    def cleanup(self):
        pass

    def setup(self):
        self._game=self.game
        if not self.use_multigame:
            self.game=AutoResetGame(self.game)
        
        self.worldapi=self.game.reset(seed=0)
        self.player.reset(seed=0)
        self.player(self.worldapi,**self.player_args)
        self._node_path=None
        

class NavViewer:
    def __init__(self,first_person,use_multigame=False):
        self.use_multigame=use_multigame
        self.fp=first_person

    def play(self, game, player, player_args, _game_dt, _game_n_steps, view_all_steps):
        key_map = {
            "z": "forward",
            "s": "reverse",
            "q": "turnLeft",
            "d": "turnRight",
            "x": "jump",
        }
        viewer = PandaShowBase(
            game, player, self.use_multigame, player_args, key_map, _game_dt, _game_n_steps, view_all_steps,self.fp
        )
        viewer.setup()
        viewer.run()

@hydra.main(config_path="./yaml", config_name="run.yaml")
def main(cfg):
    game = instantiate_class(cfg.game)

    player = instantiate_class(cfg.player)
    player_args = {}
    if "player_args" in cfg:
        player_args = cfg.player_args
    viewer = instantiate_class(cfg.viewer)
    viewer.play(
        game, player, player_args, cfg._game_dt, cfg._game_n_steps, cfg._view_all_steps
    )


if __name__ == "__main__":
    main()

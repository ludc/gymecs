from gymecs import GymEnv
import sys
import time

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
    ):
        super().__init__()
        self.game = game
        
        base.setBackgroundColor(0.1, 0.1, 0.1, 1)
        base.setFrameRateMeter(True)
        
        base.cam.setPos(0, -60, 4)
        base.cam.lookAt(5, 0, 0)

        # Light
        alight = AmbientLight("ambientLight")
        alight.setColor(Vec4(0.5, 0.5, 0.5, 1))
        alightNP = render.attachNewNode(alight)

        # dlight = PointLight("directionalLight")
        dlight = DirectionalLight("...")
        dlight.setDirection(Vec3(0, -1, -1))
        dlight.setColor(Vec4(0.4, 0.7, 0.7, 1))
        dlight.setShadowCaster(True,2048,2048)
        render.setShaderAuto()
        dlightNP = render.attachNewNode(dlight)
        dlightNP.setPos(0.0,0.0,20.0)

        render.clearLight()
        render.setShaderAuto()
        render.setLight(dlightNP)
        render.setLight(alightNP)

        self.accept("escape", self.doExit)
        self._node_path=None

    def doExit(self):
        self.cleanup()
        sys.exit(1)

    def update(self):        
        gnp=self.game.world().get_np()
        if self._node_path!=gnp:
            if not self._node_path is None: self._node_path.removeNode()
            self._node_path=gnp
            self._node_path.reparentTo(render)

    def cleanup(self):
        pass


class GymEnv3D(GymEnv):
    def __init__(self,game,step_arguments={}):
        super().__init__(game,step_arguments)
        self.viewer=None
        
        
    def render(self,**arguments):
        if self.viewer is None: self.viewer=PandaShowBase(self._game)
        self.viewer.update()
        taskMgr.step()

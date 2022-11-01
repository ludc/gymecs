from gymecs import Component,Entity,System
from raylib import ffi, rl, colors
import pyray as pr
import collections

class RayLibDrawComponent(Component):
    """ A component that can execute raylib commands

    Args:
        Component (_type_): _description_
    """  
    draw_layer:int=0 # The draw layer to define execution order
    activated:bool=True # If False, the component is not executed

    def __init__(self,**values):
        super().__init__(**values)

    def _draw(self,entity):
        raise NotImplementedError

class RayLibRectangle(RayLibDrawComponent):
    """ Draw a cube based on the position value.
    """    
    size:list=[0.0,0.0,0.0]
    color:list=[255,255,255,255]
    position:list=[0.0,0.0,0.0]

    def _draw(self,entity):
        position = pr.Vector3(*self.position)
        color = pr.Color(*self.color)
        rl.DrawCube(position, self.size[0],self.size[1],self.size[2], color)

class RayLibBackground(RayLibDrawComponent):
    color=colors.WHITE
    draw_layer=-1000

    def _draw(self,entity):
        rl.ClearBackground(self.color) 

class RayLibCamera(RayLibDrawComponent):
    position:list=[-30.0,-30.0,18.0]
    target:list=[0.0,0.0,0.0]
    up:list=[0.0, 0.0, 1.0]
    fovy= 45.0    
    projection=rl.CAMERA_PERSPECTIVE
    camera=None
    draw_layer=-10
    
    def _draw(self,entity):
        if self.camera is None:
            self.camera = pr.Camera3D(self.position,self.target,self.up,self.fovy, self.projection)
            pr.set_camera_mode(self.camera, pr.CAMERA_CUSTOM)
        else:
            self.camera.position=pr.Vector3(*self.position)
            self.camera.target=pr.Vector3(*self.target)
            self.camera.up=pr.Vector3(*self.up)            
        pr.begin_mode_3d(self.camera)

class RayLibSystem(System):
    def __init__(self,screen_size,screen_title="gymECS",camera_mode=rl.CAMERA_PERSPECTIVE,debug=False):
        self._screen_size=screen_size
        self._screen_title=screen_title
        self._first_run=True
        self._camera_mode=camera_mode
        self._debug=debug
        self.__memory_game_dt=None

    def _first_execution(self,world,_game_dt=None,**arguments):            
            rl.InitWindow(self._screen_size[0], self._screen_size[1], bytes(self._screen_title, 'utf-8'))
            self.__memory_game_dt=_game_dt
            if not _game_dt is None and _game_dt>0.0:
                print("Fixing FPS at: ",_game_dt)
                rl.SetTargetFPS(int(1.0/_game_dt))    
            self._first_run=False            

    def __call__(self,world,_game_dt=None,**arguments):
        """ Draw the raylib components

        Args:
            world (World): the world to draw
            _game_dt (float, optional): tme in seconds between two frames
        """        
        if not self.__memory_game_dt is None:
            assert _game_dt is None or self.__memory_game_dt==_game_dt,"Cannot change FPS during game."
        
        if self._first_run:
            self._first_execution(world,_game_dt,**arguments)
        rl.BeginDrawing()
        entity_component_names=[k for k in world.get_components_by_type(RayLibDrawComponent)]

        # Order by draw_layer
        by_layer={}
        for ((ename,entity),(cname,component)) in entity_component_names:
            layer=component.draw_layer
            if not layer in by_layer: by_layer[layer]=[]
            by_layer[layer].append(((ename,entity),(cname,component)) )
        ordered = collections.OrderedDict(sorted(by_layer.items()))
        
        for l,c in ordered.items():                                    
            for (ename,entity),(cname,component) in c:
                component._draw(entity)
                if self._debug: print("Draw: ",ename,cname)        
        pr.end_mode_3d()
        #rl.EndMode3D()
        rl.EndDrawing()
            

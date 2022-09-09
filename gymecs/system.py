class System:
    def __call__(self,worldapi,**arguments):
        self._execute(worldapi,**arguments)
        worldapi.flush()

    def _execute(self,worldapi,**arguments):        
        raise NotImplementedError

class LocalSystem:
    def __call__(self,world,**arguments):
        self._execute(world,**arguments)
        
    def _execute(self,world,**arguments):        
        raise NotImplementedError

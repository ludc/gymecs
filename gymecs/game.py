from gymecs import WorldAPI

class Game:            
    def reset(self,seed,**arguments)->WorldAPI:
        raise NotImplementedError

    def step(self,**arguments):
        raise NotImplementedError

    def is_done(self):
        raise NotImplementedError

    def world(self):
        return self._world

class AutoResetGameAPI(WorldAPI):
    def __init__(self,worldapi):
        self._worldapi=worldapi
    
    def set_entity(self,name,entity):
        self._worldapi.set_entity(name,entity)
    
    def del_entity(self,name):
        self._worldapi.del_entity(name)
    
    def set_component(self,name,name_component,component):
        self._worldapi.set_component(name,name_component,component)

    def get_component(self,name,name_component):
        return self._worldapi.get_component(name,name_component)

    def query(self,query):
        return self._worldapi.query(query)
    
    def update(self,update):
        self._worldapi.update(update)
    
    def flush(self):
        self._worldapi.flush()
    
    def _change_api(self,worldapi):
        assert isinstance(worldapi,WorldAPI)
        self._worldapi=worldapi

class AutoResetGame(Game):
    def __init__(self,game):
        self.game=game        

    def reset(self,seed,**arguments):
        wapi=self.game.reset(seed=seed,**arguments)
        self.seed=seed
        self.to_reset=False
        self.worldapi=AutoResetGameAPI(wapi)
        return self.worldapi

    def step(self,**arguments):
        if self.to_reset:
            self.seed+=1
            wapi=self.game.reset(seed=self.seed,**arguments)
            self.worldapi._change_api(wapi)
            self.to_reset=False
            return

        self.game.step(**arguments)
        if self.game.is_done():
            self.to_reset=True

    def is_done(self):
        return False

    def world(self):
        return self.game.world()

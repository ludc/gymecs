from gymecs import WorldAPI

class Game:            
    def reset(self,seed,**arguments)->WorldAPI:
        raise NotImplementedError

    def step(self,_game_dt,**arguments):
        raise NotImplementedError

    def is_done(self):
        raise NotImplementedError

    def render(self,**arguments):
        raise NotImplementedError

class AutoResetGameAPI(WorldAPI):
    def __init__(self,worldapi):
        self._worldapi=worldapi
    
    def query(self,query):
        return self._worldapi.query(query)

    def update(self,update):
        self._worldapi.update(update)

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

    def step(self,_game_dt,**arguments):
        if self.to_reset:
            self.seed+=1
            wapi=self.game.reset(seed=self.seed,**arguments)
            self.worldapi._change_api(wapi)
            self.to_reset=False
            return

        self.game.step(_game_dt=_game_dt,**arguments)
        if self.game.is_done():
            self.to_reset=True

    def is_done(self):
        return False

    def render(self,**arguments):
        self.game.render(**arguments)

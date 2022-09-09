from gymecs.worldapi import WorldAPI

class MultiWorldApi(WorldAPI):
    def __init__(self,*apis):
        self._apis=apis
    
    def execute(self,system,**arguments):
        for api in self._apis:
            system(api,**arguments)

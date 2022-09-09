from gymecs import System


class MoveAgent(System):
    def _execute(self,worldapi,**arguments):
        agent=worldapi.get_entity("agent")
        print(agent)



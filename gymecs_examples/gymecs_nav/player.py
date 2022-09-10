# from pandac.PandaModules import loadPrcFileData
# loadPrcFileData('', 'load-display tinydisplay')
# loadPrcFileData('', 'bullet-enable-contact-events true')

import numpy as np
from drain.component import Component
from drain.processor import Processor
from drain.cast import cast_to_list
from drain.functions import F, SequentialFunction
from drain_3d import *
from drain_3d.controls import ShowBaseEventProcessor

class EventToAction(Processor):
    def __init__(self, event_id, action_id):
        super().__init__()
        self.eid = event_id
        self.aid = action_id
        self.map = {
            "forward": (0,1.0),
            "reverse": (0,-1.0),
            "turnLeft": (1,-1.0),
            "turnRight": (1,1.0),
            "jump": (2,1.0),
        }

    def _one_action(self, events):
        action = np.zeros((3))
        for e in events:
            idx,f=self.map[e]
            action[idx] += f
        return action

    def _execute(self, components, **arguments):
        events = components[self.eid]["events"]
        events = cast_to_list(events)

        if len(events) == 0 or isinstance(events[0], str):
            action = self._one_action(events)
        else:
            actions = [self._one_action(e) for e in events]
            action = np.stack(actions)
        return Component(id=self.aid, action=action)

    def is_stateless(self):
        return True

    def is_deterministic(self):
        return True


def drainnav_keyboard_player(n_repeat=0):
    from direct.showbase.InputStateGlobal import inputState

    player_function = SequentialFunction(
        F(
            ShowBaseEventProcessor(
                event_id="player/event",
                events=["forward", "reverse", "turnLeft", "turnRight", "jump"],
                inputState=inputState,
                n_repeat=n_repeat,
            )
        ),
        F(EventToAction(event_id="player/event", action_id="player/action")),
    )
    return player_function

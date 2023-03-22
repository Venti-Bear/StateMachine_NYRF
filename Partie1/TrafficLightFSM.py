from ast import Param
from typing import Optional
from state import Parameters, State
from finite_state_machine import FiniteStateMachine
from layout import Layout
from transition import Transition


class TrafficLightFSM(FiniteStateMachine):
    def __init__(self, layout: Layout, uninitialized: bool = True):
        super().__init__(layout, uninitialized)


class TrafficLightState(State):
    def __init__(self, parameters: Optional[Parameters] = Parameters(), text="TrafficLightState"):
        super().__init__(parameters)
        self.text = text
        
    def _do_in_state_action(self):
        print(self.text)
        
        
class TrafficLightTransition(Transition):
    def is_transiting(self) -> bool:
        return True


def main():
    green = TrafficLightState(text="green")
    yellow = TrafficLightState(text="yellow")
    red = TrafficLightState(text="red")
    layout = Layout()
    
    transition_g_y = TrafficLightTransition(yellow)
    transition_y_r = TrafficLightTransition(red)
    transition_r_g = TrafficLightTransition(green)
    
    green.add_transition(transition_g_y)
    yellow.add_transition(transition_y_r)
    red.add_transition(transition_r_g)
    
    s = {green, yellow, red}
    
    layout.add_states(s)
    
    fsm = FiniteStateMachine(layout)
    
    fsm.track()


if __name__ == '__main__':
    quit(main())
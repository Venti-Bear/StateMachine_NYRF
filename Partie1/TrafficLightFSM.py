from ast import Param
from base64 import encode
from time import perf_counter, sleep
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
        print(f'\r{self.text}              ', end='')


class TrafficLightTransition(Transition):
    def __init__(self, next_state: Optional[State] = None, target_time: float = 0):
        super().__init__(next_state)
        self.__target_time = target_time
        self.__start_time = None

    @property
    def is_transiting(self) -> bool:
        if self.__start_time is None:
            self.__start_time = perf_counter()

        if perf_counter() - self.__start_time > self.__target_time:
            self.__start_time = None
            return True
        else:
            return False


def main():
    parameters = Parameters()

    parameters.do_in_state_action_when_entering = True

    green = TrafficLightState(text="green", parameters=parameters)
    yellow = TrafficLightState(text="yellow", parameters=parameters)
    red = TrafficLightState(text="red", parameters=parameters)
    layout = Layout()

    transition_g_y = TrafficLightTransition(yellow, 4.0)
    transition_y_r = TrafficLightTransition(red, 1.0)
    transition_r_g = TrafficLightTransition(green, 5.0)

    green.add_transition(transition_g_y)
    yellow.add_transition(transition_y_r)
    red.add_transition(transition_r_g)

    s = {green, yellow, red}

    layout.add_states(s)

    layout.initial_state = red

    fsm = FiniteStateMachine(layout)

    fsm.run()


if __name__ == '__main__':
    quit(main())

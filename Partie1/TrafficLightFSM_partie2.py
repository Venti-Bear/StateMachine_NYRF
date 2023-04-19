from time import perf_counter
from typing import Optional
from state import Parameters, State, MonitoredState
from finite_state_machine import FiniteStateMachine
from layout import Layout
from transition import ConditionalTransition
from condition import StateEntryDurationCondition

class TrafficLight(FiniteStateMachine):
    def __init__(self):
        self.__G_TO_Y = 4.0
        self.__Y_TO_R = 1.0
        self.__R_TO_G = 5.0

        GREEN = MonitoredState()
        YELLOW = MonitoredState()
        RED = MonitoredState()
        GREEN.add_entering_action(lambda: print(f'\rGREEN', end='   '))
        YELLOW.add_entering_action(lambda: print(f'\rYELLOW', end='   '))
        RED.add_entering_action(lambda: print(f'\rRED', end='   '))

        states = {GREEN, YELLOW, RED}

        TRANS_GY = ConditionalTransition(YELLOW, StateEntryDurationCondition(self.__G_TO_Y, GREEN))
        TRANS_YR = ConditionalTransition(RED, StateEntryDurationCondition(self.__Y_TO_R, YELLOW))
        TRANS_RG = ConditionalTransition(GREEN, StateEntryDurationCondition(self.__R_TO_G, RED))

        GREEN.add_transition(TRANS_GY)
        YELLOW.add_transition(TRANS_YR)
        RED.add_transition(TRANS_RG)
        
        layout = Layout()
        layout.add_states(states)
        layout.initial_state = GREEN

        super().__init__(layout)

def main():
    traffic_light = TrafficLight()
    traffic_light.run()

if __name__ == '__main__':
    quit(main())
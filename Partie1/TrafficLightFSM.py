from finite_state_machine import FiniteStateMachine
from layout import Layout


class TrafficLightFSM(FiniteStateMachine):
    def __init__(self, layout: Layout, uninitialized: bool = True):
        super().__init__(layout, uninitialized)
from layout import Layout
from operational_state import OperationalState
from state import State
from transition import Transition

from time import perf_counter


class FiniteStateMachine:
    """todo"""

    def __init__(self, layout: Layout, uninitialized: bool = True):
        self.__layout = layout
        self.__uninitialized = uninitialized
        self.__current_applicative_state = self.__layout.initial_state
        self.__current_operationnal_state = OperationalState.UNINITIALIZED

    @property
    def current_operational_state(self) -> OperationalState:
        return self.__current_operationnal_state

    @property
    def current_applicative_state(self):
        return self.__current_applicative_state

    def reset(self):
        """sets the operational state to IDLE"""
        self.__current_operationnal_state = OperationalState.IDLE

    def _transit_by(self, transition: Transition):
        self.current_applicative_state._exec_exiting_action()
        transition._exec_transiting_action()
        self.current_applicative_state = transition.next_state
        self.current_applicative_state._exec_entering_action()

    def transit_to(self, state: State):
        self.current_applicative_state._exec_exiting_action()
        self.current_applicative_state = state
        self.current_applicative_state._exec_entering_action()

    def track(self) -> bool:
        if self.__current_operationnal_state == OperationalState.TERMINAL_REACHED:
            return False
        return True

    def run(self, reset: bool = True, time_budget: float = None):
        cur_time = perf_counter()
        prev_time = cur_time

        while self.__current_operationnal_state == OperationalState.RUNNING:
            self.track()

            cur_time = perf_counter()
            elapsed_time = cur_time - prev_time
            prev_time = cur_time

            if time_budget is not None:
                if elapsed_time >= time_budget:
                    self.__current_operationnal_state = OperationalState.IDLE

        if reset:
            self.__current_operationnal_state = OperationalState.TERMINAL_REACHED

    def stop(self):
        if self.__current_operationnal_state == OperationalState.RUNNING:
            self.__current_operationnal_state = OperationalState.IDLE

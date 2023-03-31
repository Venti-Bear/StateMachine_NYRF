from layout import Layout
from operational_state import OperationalState
from state import State
from transition import Transition

from time import perf_counter


class FiniteStateMachine:
    """todo"""

    def __init__(self, layout: Layout, uninitialized: bool = True):
        self.__layout = layout
        self.__current_applicative_state = None if uninitialized else self.__layout.initial_state
        self.__current_operational_state = OperationalState.UNINITIALIZED if uninitialized else OperationalState.IDLE

    @property
    def current_operational_state(self) -> OperationalState:
        return self.__current_operational_state

    @property
    def current_applicative_state(self):
        return self.__current_applicative_state

    def reset(self):
        """sets the operational state to IDLE"""
        self.__current_operational_state = OperationalState.IDLE
        self.__current_applicative_state = self.__layout.initial_state

    def _transit_by(self, transition: Transition):
        self.current_applicative_state._exec_exiting_action()
        transition._exec_transiting_action()
        self.__current_applicative_state = transition.next_state
        self.current_applicative_state._exec_entering_action()

    def transit_to(self, state: State):
        self.current_applicative_state._exec_exiting_action()
        self.__current_applicative_state = state
        self.current_applicative_state._exec_entering_action()

    def track(self) -> bool:
        if self.current_applicative_state.is_terminal:
            self.__current_operational_state = OperationalState.TERMINAL_REACHED
            return False

        transition = self.current_applicative_state.is_transiting
        if transition is not None:
            self._transit_by(transition)
        else:
            self.current_applicative_state._exec_in_state_action()
        
        return True

    def run(self, reset: bool = True, time_budget: float = None):
        self.__current_operational_state = OperationalState.RUNNING

        if reset:
            self.reset()

        cur_time = perf_counter()
        prev_time = cur_time

        while self.track():
            cur_time = perf_counter()
            elapsed_time = cur_time - prev_time
            prev_time = cur_time

            if time_budget is not None:
                if elapsed_time >= time_budget:
                    self.stop()
                    break

    def stop(self):
        if self.__current_operational_state == OperationalState.RUNNING:
            self.__current_operational_state = OperationalState.IDLE

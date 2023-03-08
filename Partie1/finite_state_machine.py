from layout import Layout
from operational_state import OperationalState
from state import State
from transition import Transition

from time import perf_counter


class FiniteStateMachine:
    def __init__(self, layout, uninitialized: bool = True):
        self.__layout = layout
        self.__uninitialized = uninitialized
        self.__current_applicative_state = None  # HUH?
        self.__current_operationnal_state = OperationalState.UNINITIALIZED

    @property
    def current_operational_state(self):
        return self.__current_operationnal_state

    @property
    def current_applicative_state(self):
        return self.__current_applicative_state

    def reset(self):
        self.__current_operationnal_state = OperationalState.IDLE

    def _transit_by(self, transition: Transition):
        pass

    def transit_to(self, state: State):
        pass

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
            # if reset:
            #     self.__current_operationnal_state = OperationalState.IDLE

    def stop(self):
        if self.__current_operationnal_state == OperationalState.RUNNING:
            self.__current_operationnal_state = OperationalState.IDLE

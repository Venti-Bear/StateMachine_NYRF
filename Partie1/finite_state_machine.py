from types import NoneType
from typing import Optional

from Partie1.layout import Layout
from Partie1.operational_state import OperationalState
from layout import Layout
from operational_state import OperationalState
from state import State
from transition import Transition

from time import perf_counter


class FiniteStateMachine:
    """todo"""
    __current_operational_state: OperationalState
    __current_applicative_state: Optional[State]
    __layout: Layout

    def __init__(self, layout: Layout, uninitialized: bool = True) -> None:
        if not isinstance(layout, Layout):
            raise TypeError('layout must be of type Layout')

        self.__layout = layout
        if uninitialized:
            self.__current_applicative_state = None
            self.__current_operational_state = OperationalState.UNINITIALIZED
        else:
            self.reset()

    @property
    def current_operational_state(self) -> OperationalState:
        return self.__current_operational_state

    @property
    def current_applicative_state(self) -> State:
        return self.__current_applicative_state

    def reset(self) -> None:
        """sets the operational state to IDLE"""
        self.__current_operational_state = OperationalState.IDLE
        self.__current_applicative_state = self.__layout.initial_state
        self.current_applicative_state._exec_entering_action()

    def _transit_by(self, transition: Transition) -> None:
        if not isinstance(transition, Transition):
            raise TypeError('transition must be of type Transition')

        self.current_applicative_state._exec_exiting_action()
        transition._exec_transiting_action()
        self.__current_applicative_state = transition.next_state
        self.current_applicative_state._exec_entering_action()

    def transit_to(self, state: State) -> None:
        if not isinstance(state, State):
            raise TypeError('state must be of type State')

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

    def run(self, reset: bool = True, time_budget: float = None) -> None:
        if not isinstance(reset, bool):
            raise TypeError('reset must be of type bool')
        if not isinstance(time_budget, (float, NoneType)):
            raise TypeError('time_budget must be of type float')

        self.__current_operational_state = OperationalState.RUNNING

        if reset:
            self.reset()

        start_time = perf_counter()

        while self.track():
            cur_time = perf_counter()
            elapsed_time = cur_time - start_time

            if time_budget is not None:
                if elapsed_time >= time_budget:
                    self.stop()
                    break

    def stop(self) -> None:
        if self.__current_operational_state == OperationalState.RUNNING:
            self.__current_operational_state = OperationalState.IDLE

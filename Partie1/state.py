from __future__ import annotations
from typing import Callable, Optional, List, TYPE_CHECKING, Any
import time

if TYPE_CHECKING:
    from transition import Transition


class Parameters:
    do_in_state_action_when_exiting: bool
    do_in_state_action_when_entering: bool
    terminal: bool

    def __init__(self) -> None:
        self.terminal = False
        self.do_in_state_action_when_entering = False
        self.do_in_state_action_when_exiting = False


class State:
    """todo"""
    __parameters: Parameters
    __transition: list['Transition']

    def __init__(self, parameters: Parameters = Parameters()) -> None:
        if not isinstance(parameters, Parameters):
            raise TypeError("parameters must be a Parameters object")

        self.__transition = []
        self.__parameters = parameters

    @property
    def is_valid(self) -> bool:
        """todo"""
        if len(self.__transition) == 0:
            return False

        return all((transition.is_valid for transition in self.__transition))

    @property
    def is_terminal(self) -> bool:
        """todo"""
        return self.__parameters.terminal

    @property
    def is_transiting(self) -> Optional['Transition']:
        """todo"""
        for transition in self.__transition:
            if transition.is_transiting:
                return transition

    def add_transition(self, transition: 'Transition') -> None:
        """todo"""
        from transition import Transition
        if not isinstance(transition, Transition):
            raise TypeError("transition must be a Transition object")

        self.__transition.append(transition)

    def _exec_entering_action(self) -> None:
        """todo"""
        self._do_entering_action()

        if self.__parameters.do_in_state_action_when_entering:
            self._exec_in_state_action()

    def _exec_in_state_action(self) -> None:
        """todo"""
        self._do_in_state_action()

    def _exec_exiting_action(self) -> None:
        """todo"""
        if self.__parameters.do_in_state_action_when_exiting:
            self._exec_in_state_action()

        self._do_exiting_action()

    def _do_entering_action(self) -> None:
        """todo"""

    def _do_in_state_action(self) -> None:
        """todo"""

    def _do_exiting_action(self) -> None:
        """todo"""

    def __hash__(self) -> int:
        # not sure if this is needed:
        # https://stackoverflow.com/questions/11324271/what-is-the-default-hash-in-python#comment14907554_11324351
        return hash(id(self))


class ActionState(State):
    __exiting_action: list[Callable[[], None]]
    __in_state_action: list[Callable[[], None]]
    __entering_action: list[Callable[[], None]]

    def __init__(self, parameters: Parameters = Parameters()) -> None:
        super().__init__(parameters)
        self.__entering_action = []
        self.__in_state_action = []
        self.__exiting_action = []

    def _do_entering_action(self) -> None:
        """TODO"""
        for entering_action in self.__entering_action:
            entering_action()

    def _do_in_state_action(self) -> None:
        """TODO"""
        for in_state_action in self.__in_state_action:
            in_state_action()

    def _do_exiting_action(self) -> None:
        """TODO"""
        for exiting_action in self.__exiting_action:
            exiting_action()

    def add_entering_action(self, action: Callable[[], None]) -> None:
        if not isinstance(action, Callable):
            raise Exception("action must be callable.")
        else:
            self.__entering_action.append(action)

    def add_in_state_action(self, action: Callable[[], None]) -> None:
        if not isinstance(action, Callable):
            raise Exception("action must be callable.")
        else:
            self.__in_state_action.append(action)

    def add_exiting_action(self, action: Callable[[], None]) -> None:
        if not isinstance(action, Callable):
            raise Exception("action must be callable.")
        else:
            self.__exiting_action.append(action)


class MonitoredState(ActionState):
    custom_value: Any
    __entry_count: int
    __counter_last_exit: float
    __counter_last_entry: float

    def __init__(self, parameters: Parameters = Parameters()) -> None:
        super().__init__(parameters)
        self.__counter_last_entry = 0.0
        self.__counter_last_exit = 0.0
        self.__entry_count = 0
        self.custom_value = None

    @property
    def entry_count(self) -> int:
        return self.__entry_count

    @property
    def last_entry_time(self) -> float:
        return self.__counter_last_entry

    @property
    def last_exit_time(self) -> float:
        return self.__counter_last_exit

    def reset_entry_count(self) -> None:
        self.__entry_count = 0

    # todo this code is suspect
    def reset_last_times(self) -> None:
        self.__counter_last_entry, self.__counter_last_exit = 0.0, 0.0

    def _exec_entering_action(self) -> None:
        self.__counter_last_entry = time.perf_counter()
        self.__entry_count += 1
        super()._exec_entering_action()

    def _exec_exiting_action(self) -> None:
        self.__counter_last_exit = time.perf_counter()
        super()._exec_exiting_action()

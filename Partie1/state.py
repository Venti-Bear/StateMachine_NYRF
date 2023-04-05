from __future__ import annotations
from typing import Callable, Optional, List, TYPE_CHECKING
import time

if TYPE_CHECKING:
    from transition import Transition


class Parameters:
    def __init__(self):
        self.terminal: bool = False
        self.do_in_state_action_when_entering: bool = False
        self.do_in_state_action_when_exiting: bool = False


class State:
    """todo"""

    def __init__(self, parameters: Optional[Parameters] = Parameters()):
        self.__transition: List[Transition] = []
        self.__parameters: Parameters = parameters

    @property
    def is_valid(self) -> bool:
        """todo"""
        if len(self.__transition) == 0:
            return False

        return all((transition.is_valid() for transition in self.__transition))

    @property
    def is_terminal(self) -> bool:
        """todo"""
        return self.__parameters.terminal

    @property
    def is_transiting(self):
        """todo"""
        for transition in self.__transition:
            if transition.is_transiting:
                return transition

    def add_transition(self, transition: Transition):
        """todo"""
        self.__transition.append(transition)

    def _exec_entering_action(self):
        """todo"""
        self._do_entering_action()

        if self.__parameters.do_in_state_action_when_entering:
            self._exec_in_state_action()

    def _exec_in_state_action(self):
        """todo"""
        self._do_in_state_action()

    def _exec_exiting_action(self):
        """todo"""
        if self.__parameters.do_in_state_action_when_exiting:
            self._exec_in_state_action()

        self._do_exiting_action()

    def _do_entering_action(self):
        """todo"""

    def _do_in_state_action(self):
        """todo"""

    def _do_exiting_action(self):
        """todo"""

    def __hash__(self):
        # not sure if this is needed:
        # https://stackoverflow.com/questions/11324271/what-is-the-default-hash-in-python#comment14907554_11324351
        return hash(id(self))
    
class ActionState(State):
    def __init__(self, parameters: Parameters = Parameters()):
        super().__init__(parameters)
        self.__entering_action: List[Callable[[], None]] = []
        self.__in_state_action: List[Callable[[], None]] = []
        self.__exiting_action: List[Callable[[], None]] = []
    
    def _do_entering_action(self) -> None:
        '''TODO'''
        for entering_action in self.__entering_action:
            entering_action()
    
    def _do_in_state_action(self) -> None:
        '''TODO'''
        for in_state_action in self.__in_state_action:
            in_state_action()
    
    def _do_exiting_action(self) -> None:
        '''TODO'''
        for exiting_action in self.__exiting_action:
            exiting_action()

    def add_entering_action(self, action: Callable[[], None]):
        if not isinstance(action, Callable[[], None]):
            raise Exception("action must be callable.")
        else:
            self.__entering_action.append(action)

    def add_in_state_action(self, action: Callable[[], None]):
        if not isinstance(action, Callable[[], None]):
            raise Exception("action must be callable.")
        else:
            self.__in_state_action.append(action)
        
    def add_exiting_action(self, action: Callable[[], None]):
        if not isinstance(action, Callable[[], None]):
            raise Exception("action must be callable.")
        else:
            self.__exiting_action.append(action)

class MonitoredState(ActionState):
    def __init__(self, parameters: Parameters = Parameters()):
        super().__init__(parameters)
        self.__counter_last_entry: float = 0.0
        self.__counter_last_exit: float = 0.0
        self.__entry_count: int = 0
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
    
    def reset_last_times(self) -> None:
        self.__counter_last_entry, self.__counter_last_exit = 0.0

    def _exec_entering_action(self) -> None:
        self.__counter_last_entry = time.perf_counter()
        self.__entry_count += 1
        super().__entering_action()
    
    def _exec_exiting_action(self) -> None:
        self.__counter_last_exit = time.perf_counter()
        super().__exiting_action()

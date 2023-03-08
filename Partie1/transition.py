from abc import ABC
import abc
from typing import Optional
from state import State


class Transition(ABC):
    def __init__(self, next_state: Optional[State] = None):
        self.__next_state: State = next_state

    def is_valid(self) -> bool:
        return self.__next_state is not None

    @property
    def next_state(self) -> Optional[State]:
        return self.__next_state
        
    @next_state.setter
    def next_state(self, next_state: Optional[State]):
        self.__next_state = next_state

    @abc.abstractmethod
    @property
    def is_transiting(self) -> bool:
        raise NotImplementedError

    def _exec_transiting_action(self):
        pass

    def _do_transiting_action(self):
        pass

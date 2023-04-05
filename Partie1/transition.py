from abc import ABC
import abc
from argparse import Action
from types import NoneType
from typing import Callable, Optional
from state import State


class Transition(ABC):
    def __init__(self, next_state: Optional[State] = None):
        if not isinstance(next_state, (State, NoneType)):
            raise TypeError('next_state must be of type State')

        self.__next_state: State = next_state

    def is_valid(self) -> bool:
        return self.__next_state is not None

    @property
    def next_state(self) -> Optional[State]:
        return self.__next_state

    @next_state.setter
    def next_state(self, next_state: Optional[State]):
        if not isinstance(next_state, (State, NoneType)):
            raise TypeError('next_state must be of type State')

        self.__next_state = next_state

    @property
    @abc.abstractmethod
    def is_transiting(self) -> bool:
        raise NotImplementedError

    def _exec_transiting_action(self):
        self._do_transiting_action()

    def _do_transiting_action(self):
        pass


# TYPE HINTING À FAIRE
class ConditionalTransition(Transition):
    def __init__(self, next_state: Optional[State] = None, condition=None):
        super().__init__(next_state)
        self.__condition = condition

    def is_valid(self) -> bool:
        return super.is_valid() and self.__condition is not None

    @property
    def condition(self):
        return self.__condition

    @condition.setter
    def condition(self, condition):
        self.__condition = condition

    def is_transiting(self) -> bool:
        """todo"""
        return super().is_transiting


class ActionTransition(ConditionalTransition):
    def __init__(self, next_state: Optional[State] = None, condition=None):
        super().__init__(next_state, condition)
        self.__transiting_actions = list[Callable[[], None]]
        
    def _do_transiting_action(self):
        return super()._do_transiting_action()
    
    def add_transition_action(self, action: Callable[[], None]) -> None:
        self.__transiting_actions.append(action)


class MonitoredTransition(ActionTransition):
    def __init__(self, next_state: Optional[State] = None, condition=None):
        super().__init__(next_state, condition)
        self.__transit_count = 0
        self.__last_transit_time = 0.
        self.custom_value = any
        
    @property
    def transit_count(self) -> int:
        return self.__transit_count
    
    @property
    def last_transit_time(self) -> float:
        return self.__last_transit_time
    
    def reset_transit_count(self) -> None:
        self.__transit_count = 0
        
    def reset_last_transit_time(self) -> None:
        self.__last_transit_time = 0
        
    def _exec_transiting_action(self):
        return super()._exec_transiting_action()

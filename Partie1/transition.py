from abc import ABC
import abc
import time
from typing import Callable, Optional, List, Any, TYPE_CHECKING

from condition import Condition

if TYPE_CHECKING:
    from state import State

NoneType = type(None)


class Transition(ABC):
    __next_state: Optional['State']

    def __init__(self, next_state: Optional['State'] = None) -> None:
        from state import State
        if not isinstance(next_state, State) and next_state is not None:
            raise TypeError('next_state must be of type State')

        self.__next_state = next_state

    @property
    def is_valid(self) -> bool:
        return self.__next_state is not None

    @property
    def next_state(self) -> Optional['State']:
        return self.__next_state

    @next_state.setter
    def next_state(self, next_state: Optional['State']) -> None:
        from state import State
        if not isinstance(next_state, (State, NoneType)):
            raise TypeError('next_state must be of type State')

        self.__next_state = next_state

    @property
    @abc.abstractmethod
    def is_transiting(self) -> bool:
        raise NotImplementedError

    def _exec_transiting_action(self) -> None:
        self._do_transiting_action()

    def _do_transiting_action(self) -> None:
        ...


class ConditionalTransition(Transition):
    __condition: Optional[Condition]

    def __init__(self, next_state: Optional['State'] = None, condition: Optional[Condition] = None) -> None:
        super().__init__(next_state)

        if not isinstance(condition, (Condition, NoneType)):
            raise TypeError('condition must be of type Condition or None')

        self.__condition: Optional[Condition] = condition

    def is_valid(self) -> bool:
        return super().is_valid and self.__condition is not None

    @property
    def condition(self) -> Optional[Condition]:
        return self.__condition

    @condition.setter
    def condition(self, condition: Optional[Condition]) -> None:
        if not isinstance(condition, Condition):
            raise TypeError("condition must be a Condition object or None")
        self.__condition = condition

    @property
    def is_transiting(self) -> bool:
        """todo"""
        return bool(self.__condition)


class ActionTransition(ConditionalTransition):
    __transiting_actions: list[Callable[[], None]]

    def __init__(self, next_state: Optional['State'] = None, condition: Optional[Condition] = None) -> None:
        super().__init__(next_state, condition)
        self.__transiting_actions = []

    def _do_transiting_action(self) -> None:
        for action in self.__transiting_actions:
            action()

    def add_transition_action(self, action: Callable[[], None]) -> None:
        if not isinstance(action, Callable):
            raise TypeError("action must be callable")

        self.__transiting_actions.append(action)


class MonitoredTransition(ActionTransition):
    custom_value: Any
    __last_transit_time: float
    __transit_count: int

    def __init__(self, next_state: Optional['State'] = None, condition: Optional[Condition] = None) -> None:
        super().__init__(next_state, condition)
        self.__transit_count = 0
        self.__last_transit_time = 0.
        self.custom_value = None

    @property
    def transit_count(self) -> int:
        return self.__transit_count

    @property
    def last_transit_time(self) -> float:
        return self.__last_transit_time

    # todo this code is suspect
    def reset_transit_count(self) -> None:
        self.__transit_count = 0

    def reset_last_transit_time(self) -> None:
        self.__last_transit_time = 0.

    def _exec_transiting_action(self) -> None:
        self.__transit_count += 1
        self.__last_transit_time = time.perf_counter()
        return super()._exec_transiting_action()

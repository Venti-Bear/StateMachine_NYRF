from types import NoneType
from typing import List, Optional, Any
from state import MonitoredState
from abc import ABC
import abc
import time


class Condition(ABC):
    __inverse: bool

    def __init__(self, inverse: bool = False) -> None:
        if not isinstance(inverse, bool):
            raise TypeError("inverse must be a bool")

        self.__inverse: bool = inverse

    def __bool__(self) -> bool:
        return self.__inverse ^ self.compare()

    @abc.abstractmethod
    def compare(self) -> bool:
        ...


class AlwaysTrueCondition(Condition):
    def __init__(self, inverse: bool = False) -> None:
        super().__init__(inverse)

    def compare(self) -> bool:
        return True


class ValueCondition(Condition):
    __expected_value: Any
    __initial_value: Any

    def __init__(self, initial_value: Any, expected_value: Any, inverse: bool = False) -> None:
        super().__init__(inverse)
        self.__initial_value = initial_value
        self.__expected_value = expected_value

    def compare(self) -> bool:
        return self.__initial_value == self.__expected_value


class TimedCondition(Condition):
    __duration: float
    __time_reference: float

    def __init__(self, duration: float = 1.0, time_reference: Optional[float] = None, inverse: bool = False) -> None:
        if not isinstance(duration, float):
            raise TypeError("duration must be a float")
        if not isinstance(time_reference, (NoneType, float)):
            raise TypeError("time_reference must be a float or None")

        super().__init__(inverse)
        self.__duration = duration

        if time_reference is None:
            self.__time_reference = time.perf_counter()
        else:
            self.__time_reference = time_reference

    @property
    def duration(self) -> float:
        return self.__duration

    @duration.setter
    def duration(self, value) -> None:
        self.__duration = value

    def compare(self) -> bool:
        return time.perf_counter() - self.__time_reference < self.__duration

    def reset(self) -> None:
        self.__time_reference = time.perf_counter()


class MonitoredStateCondition(Condition, ABC):
    _monitored_state: MonitoredState

    def __init__(self, monitored_state: MonitoredState, inverse: bool = False) -> None:
        if not isinstance(monitored_state, MonitoredState):
            raise TypeError("monitored_state must be a MonitoredState object")

        super().__init__(inverse)
        self._monitored_state = monitored_state

    @property
    def monitored_state(self) -> MonitoredState:
        return self._monitored_state

    @monitored_state.setter
    def monitored_state(self, value: MonitoredState) -> None:
        if not isinstance(value, MonitoredState):
            raise TypeError("value must be a MonitoredState object")

        self._monitored_state = value


class StateEntryDurationCondition(MonitoredStateCondition):
    __duration: float

    def __init__(self, duration: float, monitored_state: MonitoredState, inverse: bool = False):
        if not isinstance(duration, float):
            raise TypeError("duration must be a float")

        super().__init__(monitored_state, inverse)
        self.__duration = duration

    @property
    def duration(self) -> float:
        return self.__duration

    @duration.setter
    def duration(self, duration) -> None:
        self.__duration = duration

    def compare(self) -> bool:
        return self.__duration < time.perf_counter() - self._monitored_state.last_entry_time


class StateEntryCountCondition(MonitoredStateCondition):
    __expected_count: int
    __auto_reset: bool

    def __init__(self, expected_count: int, monitored_state: MonitoredState, auto_reset: bool = True,
                 inverse: bool = False) -> None:
        if not isinstance(expected_count, int):
            raise TypeError("expected_count must be a int")
        if not isinstance(auto_reset, bool):
            raise TypeError("auto_reset must be a bool")

        super().__init__(monitored_state, inverse)
        self.__auto_reset: bool = auto_reset
        self.__expected_count: int = expected_count

    def compare(self) -> bool:
        if self.__expected_count <= self._monitored_state.entry_count:
            if self.__auto_reset:
                self.reset_count()
            return True
        return False

    def reset_count(self) -> None:
        self._monitored_state.reset_entry_count()


class StateValueCondition(MonitoredStateCondition):
    __expected_value: Any

    def __init__(self, expected_value: Any, monitored_state: MonitoredState, inverse: bool = False) -> None:
        super().__init__(monitored_state, inverse)
        self.__expected_value = expected_value

    @property
    def expected_value(self) -> MonitoredState:
        return self.__expected_value

    @expected_value.setter
    def expected_value(self, value: Any) -> None:
        self.__expected_value = value

    def compare(self) -> bool:
        return self.__expected_value == self._monitored_state.custom_value


class ManyConditions(Condition, ABC):
    _condition_list: list[Condition]

    def __init__(self, inverse: bool = False) -> None:
        super().__init__(inverse)
        self._condition_list = []

    def add_condition(self, condition) -> None:
        if not isinstance(condition, Condition):
            raise TypeError("condition must be a Condition object")

        self._condition_list.append(condition)

    def add_conditions(self, condition_list: List[Condition]) -> None:
        if not isinstance(condition_list, List):
            raise TypeError("condition_list must be a list")

        for condition in condition_list:
            self._condition_list.append(condition)


class AllConditions(ManyConditions):
    def __init__(self, inverse: bool = False):
        super().__init__(inverse)

    def compare(self) -> bool:
        return all(self._condition_list)


class AnyConditions(ManyConditions):
    def __init__(self, inverse: bool = False) -> None:
        super().__init__(inverse)

    def compare(self) -> bool:
        return any(self._condition_list)


class NoneConditions(ManyConditions):
    def __init__(self, inverse: bool = False) -> None:
        super().__init__(inverse)

    def compare(self) -> bool:
        return not any(self._condition_list)

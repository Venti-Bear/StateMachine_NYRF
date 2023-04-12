from typing import List, Optional
from state import MonitoredState
from abc import ABC
import abc
import time


class Condition(ABC):
    def __init__(self, inverse: bool = False):
        self.__inverse: bool = inverse

    def __bool__(self) -> bool:
        return self.__inverse ^ self.compare()

    @abc.abstractmethod
    def compare(self) -> bool:
        ...


class AlwaysTrueCondition(Condition):
    def __init__(self, inverse: bool = False):
        super().__init__(inverse)

    def compare(self) -> bool:
        return True


class ValueCondition(Condition):
    def __init__(self, initial_value: any, expected_value: any, inverse: bool = False):
        super().__init__(inverse)
        self.__initial_value: any = initial_value
        self.__expected_value: any = expected_value

    def compare(self) -> bool:
        return self.__initial_value == self.__expected_value


class TimedCondition(Condition):
    def __init__(self, duration: float = 1.0, time_reference: Optional[float] = None, inverse: bool = False):
        super().__init__(inverse)
        self.__duration = duration
        self.__time_reference = time_reference

    @property
    def duration(self) -> float:
        return self.__duration

    @duration.setter
    def duration(self, value) -> None:
        self.__duration = value

    def compare(self):
        return time.perf_counter() - self.__time_reference < self.__duration

    def reset(self):
        self.__time_reference = time.perf_counter()


class MonitoredStateCondition(Condition, ABC):
    def __init__(self, monitored_state: MonitoredState, inverse: bool = False):
        super().__init__(inverse)
        self.__monitored_state: MonitoredState = monitored_state

    @property
    def monitored_state(self) -> MonitoredState:
        return self.__monitored_state

    @monitored_state.setter
    def monitored_state(self, value) -> None:
        self.__monitored_state = value


class StateEntryDurationCondition(MonitoredStateCondition):
    def __init__(self, duration: float, monitored_state: MonitoredState, inverse: bool = False):
        super().__init__(monitored_state, inverse)
        self.__duration: float = duration

    @property
    def duration(self) -> MonitoredState:
        return self.__monitored_state

    @duration.setter
    def duration(self, duration) -> None:
        self.__duration = duration

    def compare(self) -> bool:
        return self.__duration > time.perf_counter() - self.__monitored_state.last_entry_time


class StateEntryCountCondition(MonitoredStateCondition):
    def __init__(self, expected_count: int, monitored_state: MonitoredState, auto_reset: bool = True,
                 inverse: bool = False):
        super().__init__(monitored_state, inverse)
        self.__auto_reset: bool = auto_reset
        self.__expected_count: int = expected_count

    def compare(self) -> bool:
        if self.__expected_count >= self.__monitored_state.entry_count:
            if self.__auto_reset:
                self.reset_count()
            return True
        return False

    def reset_count(self) -> None:
        self.__monitored_state.reset_entry_count()


class StateValueCondition(MonitoredStateCondition):
    def __init__(self, expected_value: None, monitored_state: MonitoredState, inverse: bool = False):
        super().__init__(monitored_state, inverse)
        self.__expected_value: None = expected_value

    @property
    def expected_value(self) -> MonitoredState:
        return self.__expected_value

    @expected_value.setter
    def expected_value(self, value) -> None:
        self.__expected_value = value

    def compare(self) -> bool:
        return self.__expected_value == self.__monitored_state.custom_value


class ManyConditions(Condition, ABC):
    def __init__(self, inverse: bool = False):
        super().__init__(inverse)
        self._condition_list: List[Condition] = []

    def add_condition(self, condition) -> None:
        self._condition_list.append(condition)

    def add_conditions(self, condition_list) -> None:
        for condition in condition_list:
            self._condition_list.append(condition)


class AllConditions(ManyConditions):
    def __init__(self, inverse: bool = False):
        super().__init__(inverse)

    def compare(self) -> bool:
        return all(self._condition_list)


class AnyConditions(ManyConditions):
    def __init__(self, inverse: bool = False):
        super().__init__(inverse)

    def compare(self) -> bool:
        return any(self._condition_list)


class NoneConditions(ManyConditions):
    def __init__(self, inverse: bool = False):
        super().__init__(inverse)

    def compare(self) -> bool:
        return not any(self._condition_list)

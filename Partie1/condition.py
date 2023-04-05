from state import MonitoredState
from abc import ABC
import abc

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
    def __init__(self, initial_value: None, expected_value: None, inverse: bool = False):
        super().__init__(inverse)
        self.__initial_value: None = initial_value
        self.__expected_value: None = expected_value
    
    def compare(self) -> bool:
        return self.__initial_value == self.__expected_value
    

class TimedCondition(Condition):
    def __init__(self, duration: float = 1.0, time_reference: float = None, inverse: bool = False)
        super().__init__(inverse)
        self.__duration = duration
        self.__time_reference = time_reference

    @property
    def duration(self) -> float:
        return self.__duration
    
    @duration.setter
    def set_duration(self, value) -> None:
        self.__duration = value

    def reset(self):
        self.__time_reference = 0.0


class MonitoredStateCondition(Condition):
    def __init__(self, monitored_state: MonitoredState, inverse: bool = False):
        super().__init__(inverse)
        self.__monitored_state: MonitoredState = monitored_state

    @property
    def monitored_state(self) -> MonitoredState:
        return self.__monitored_state
    
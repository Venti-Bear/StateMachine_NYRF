from typing import List, Optional, Any, TYPE_CHECKING
from abc import ABC
import abc
import time

if TYPE_CHECKING:
    from state import MonitoredState


class Condition(ABC):
    """
    Abstract base class representing a condition that can be evaluated to a boolean value.

    Attributes:
        __inverse (bool): A private boolean flag indicating whether the condition's boolean value should be inverted.
    """
    __inverse: bool

    def __init__(self, inverse: bool = False) -> None:
        """
        Initializes a new Condition object with the specified inverse flag.

        Args:
            inverse (bool): Optional boolean flag indicating whether the condition's boolean value should be inverted.
                            Defaults to False.

        Raises:
            TypeError: If inverse is not a boolean value.
        """
        if not isinstance(inverse, bool):
            raise TypeError("inverse must be a bool")

        self.__inverse: bool = inverse

    def __bool__(self) -> bool:
        """
        Returns the boolean value of the condition after applying the inverse flag.

        Returns:
            bool: The boolean value of the condition after applying the inverse flag.
        """
        return self.__inverse ^ self.compare()

    @abc.abstractmethod
    def compare(self) -> bool:
        """
        Abstract method that must be overridden by child classes to perform the condition evaluation.

        Returns:
            bool: The boolean result of the condition evaluation.
        """
        ...


class AlwaysTrueCondition(Condition):
    """
    A concrete subclass of the Condition abstract base class that always evaluates to True.
    """
    def __init__(self, inverse: bool = False) -> None:
        """
        Initializes a new AlwaysTrueCondition object with the specified inverse flag.

        Args:
            inverse (bool): Optional boolean flag indicating whether the condition's boolean value should be inverted.
                            Defaults to False.
        """
        super().__init__(inverse)

    def compare(self) -> bool:
        """
        Returns True, as this condition is always true.

        Returns:
            bool: Always returns True.
        """
        return True


class ValueCondition(Condition):
    """
    A concrete subclass of the Condition abstract base class that checks whether a value matches an expected value.

    Attributes:
        __expected_value (Any): The expected value to compare against.
        __initial_value (Any): The initial value to compare against the expected value.
    """
    __expected_value: Any
    __initial_value: Any

    def __init__(self, initial_value: Any, expected_value: Any, inverse: bool = False) -> None:
        """
        Initializes a new ValueCondition object with the specified initial and expected values and optional inverse flag.

        Args:
            initial_value (Any): The initial value to compare against the expected value.
            expected_value (Any): The expected value to compare against the initial value.
            inverse (bool): Optional boolean flag indicating whether the condition's boolean value should be inverted.
                            Defaults to False.
        """
        super().__init__(inverse)
        self.__initial_value = initial_value
        self.__expected_value = expected_value

    def compare(self) -> bool:
        """
        Compares the initial value with the expected value and returns the result as a boolean value.

        Returns:
            bool: True if the initial value matches the expected value, False otherwise.
        """
        return self.__initial_value == self.__expected_value


class TimedCondition(Condition):
    """
    A concrete subclass of the Condition abstract base class that checks whether a certain amount of time has elapsed.

    Attributes:
        __duration (float): The duration of time to wait before the condition becomes True.
        __time_reference (float): The time reference from which to start counting.
    """
    __duration: float
    __time_reference: float

    def __init__(self, duration: float = 1.0, time_reference: Optional[float] = None, inverse: bool = False) -> None:
        """
        Initializes a new TimedCondition object with the specified duration, time reference and optional inverse flag.

        Args:
            duration (float): The duration of time to wait before the condition becomes True.
            time_reference (float, optional): Optional time reference from which to start counting.
                                              If None, the current time will be used as the reference.
            inverse (bool): Optional boolean flag indicating whether the condition's boolean value should be inverted.
                            Defaults to False.
        """
        if not isinstance(duration, float):
            raise TypeError("duration must be a float")
        if time_reference is None:
            raise TypeError("time_reference must be a float or None")

        super().__init__(inverse)
        self.__duration = duration

        if time_reference is None:
            self.__time_reference = time.perf_counter()
        else:
            self.__time_reference = time_reference

    @property
    def duration(self) -> float:
        """
        Getter method for the __duration attribute.

        Returns:
            float: The duration of time to wait before the condition becomes True.
        """
        return self.__duration

    @duration.setter
    def duration(self, value) -> None:
        """
        Setter method for the __duration attribute.

        Args:
            value (float): The new duration value to set.
        """
        self.__duration = value

    def compare(self) -> bool:
        """
        Compares the elapsed time with the duration and returns the result as a boolean value.

        Returns:
            bool: True if the elapsed time is less than the duration, False otherwise.
        """
        return time.perf_counter() - self.__time_reference < self.__duration

    def reset(self) -> None:
        """
        Resets the time reference to the current time.
        """
        self.__time_reference = time.perf_counter()


class MonitoredStateCondition(Condition, ABC):
    """
    Abstract base class for conditions that depend on a monitored state.

    Attributes:
        _monitored_state (MonitoredState): The monitored state on which the condition depends.
    """
    _monitored_state: 'MonitoredState'

    def __init__(self, monitored_state: 'MonitoredState', inverse: bool = False) -> None:
        from state import MonitoredState
        """
        Initializes a new instance of MonitoredStateCondition.

        Args:
            monitored_state (MonitoredState): The monitored state on which the condition depends.
            inverse (bool, optional): If True, the condition will be inverted. Defaults to False.

        Raises:
            TypeError: If monitored_state is not a MonitoredState object.
        """
        if not isinstance(monitored_state, MonitoredState):
            raise TypeError("monitored_state must be a MonitoredState object")

        super().__init__(inverse)
        self._monitored_state = monitored_state

    @property
    def monitored_state(self) -> 'MonitoredState':
        """
        Gets the monitored state on which the condition depends.

        Returns:
            MonitoredState: The monitored state object.
        """
        return self._monitored_state

    @monitored_state.setter
    def monitored_state(self, value: 'MonitoredState') -> None:
        from state import MonitoredState
        """
        Sets the monitored state on which the condition depends.

        Args:
            value (MonitoredState): The monitored state object.

        Raises:
            TypeError: If value is not a MonitoredState object.
        """
        if not isinstance(value, MonitoredState):
            raise TypeError("value must be a MonitoredState object")

        self._monitored_state = value


class StateEntryDurationCondition(MonitoredStateCondition):
    """
    A subclass of MonitoredStateCondition that represents a condition where the duration of the monitored state is compared
    to a specified value.

    Attributes:
    - _duration: A float representing the duration that will be compared to the monitored state.
    """
    __duration: float

    def __init__(self, duration: float, monitored_state: 'MonitoredState', inverse: bool = False):
        """
        Initializes a StateEntryDurationCondition object.

        Parameters:
        - duration: A float representing the duration that will be compared to the monitored state.
        - monitored_state: A MonitoredState object representing the state to be monitored.
        - inverse: A bool indicating whether the condition should be inverted (default is False).

        Raises:
        - TypeError: If duration is not a float or monitored_state is not a MonitoredState object.
        """
        if not isinstance(duration, float):
            raise TypeError("duration must be a float")

        super().__init__(monitored_state, inverse)
        self.__duration = duration

    @property
    def duration(self) -> float:
        """
        Gets the duration of the condition.

        Returns:
        - A float representing the duration of the condition.
        """
        return self.__duration

    @duration.setter
    def duration(self, duration) -> None:
        """
        Sets the duration of the condition.

        Parameters:
        - duration: A float representing the new duration of the condition.

        Raises:
        - TypeError: If duration is not a float.
        """
        self.__duration = duration

    def compare(self) -> bool:
        """
        Overrides the compare method of the parent class. Returns True if the difference between the current time and the
        last entry time of the monitored state is greater than the specified duration.

        Returns:
        - A bool indicating whether the condition is met.
        """
        return self.__duration < time.perf_counter() - self._monitored_state.last_entry_time


class StateEntryCountCondition(MonitoredStateCondition):
    """A Condition that checks if a MonitoredState's entry count is at least a certain value.

    Attributes:
        __auto_reset (bool): Whether or not to automatically reset the entry count when the Condition is met.
        __expected_count (int): The number of entry counts to check for.
    """
    __expected_count: int
    __auto_reset: bool

    def __init__(self, expected_count: int, monitored_state: 'MonitoredState', auto_reset: bool = True,
                 inverse: bool = False) -> None:
        """Initializes a new StateEntryCountCondition object.

        Args:
            expected_count (int): The number of entry counts to check for.
            monitored_state (MonitoredState): The MonitoredState object to monitor.
            auto_reset (bool, optional): Whether or not to automatically reset the entry count when the Condition is met.
            inverse (bool, optional): Whether to invert the Condition's result.

        Raises:
            TypeError: If expected_count is not an int or auto_reset is not a bool.
        """
        if not isinstance(expected_count, int):
            raise TypeError("expected_count must be a int")
        if not isinstance(auto_reset, bool):
            raise TypeError("auto_reset must be a bool")

        super().__init__(monitored_state, inverse)
        self.__auto_reset: bool = auto_reset
        self.__expected_count: int = expected_count

    def compare(self) -> bool:
        """Compares the monitored State's entry count with the expected count.

        Returns:
            bool: True if the entry count meets or exceeds the expected count, False otherwise.
        """
        if self.__expected_count <= self._monitored_state.entry_count:
            if self.__auto_reset:
                self.reset_count()
            return True
        return False

    def reset_count(self) -> None:
        """Resets the monitored State's entry count."""
        self._monitored_state.reset_entry_count()


class StateValueCondition(MonitoredStateCondition):
    """
    A condition that checks if the custom value of a monitored state matches a specific expected value.

    Attributes:
        expected_value (Any): The expected value that the custom value of the monitored state should match.
    """
    __expected_value: Any

    def __init__(self, expected_value: Any, monitored_state: 'MonitoredState', inverse: bool = False) -> None:
        """
        Initializes a new instance of the StateValueCondition class.

        Args:
            expected_value (Any): The expected value that the custom value of the monitored state should match.
            monitored_state (MonitoredState): The monitored state to check.
            inverse (bool, optional): Whether to invert the result of the condition. Defaults to False.
        """
        super().__init__(monitored_state, inverse)
        self.__expected_value = expected_value

    @property
    def expected_value(self) -> Any:
        """
        Any: The expected value that the custom value of the monitored state should match.
        """
        return self.__expected_value

    @expected_value.setter
    def expected_value(self, value: Any) -> None:
        """
        Sets the expected value that the custom value of the monitored state should match.

        Args:
            value (Any): The expected value.
        """
        self.__expected_value = value

    def compare(self) -> bool:
        """
        Compares the custom value of the monitored state with the expected value.

        Returns:
            bool: True if the custom value of the monitored state matches the expected value, False otherwise.
        """
        return self.__expected_value == self._monitored_state.custom_value


class ManyConditions(Condition, ABC):
    """
    Class representing a collection of conditions that are evaluated together.

    Attributes:
        _condition_list (list[Condition]): The list of conditions to be evaluated together.

    """
    _condition_list: list[Condition]

    def __init__(self, inverse: bool = False) -> None:
        """
        Initializes a ManyConditions object.

        Args:
            inverse (bool, optional): If True, the conditions will be negated. Defaults to False.
        """
        super().__init__(inverse)
        self._condition_list = []

    def add_condition(self, condition) -> None:
        """
        Adds a single condition to the ManyConditions object.

        Args:
            condition (Condition): The condition to be added.

        Raises:
            TypeError: If the condition argument is not a Condition object.
        """
        if not isinstance(condition, Condition):
            raise TypeError("condition must be a Condition object")

        self._condition_list.append(condition)

    def add_conditions(self, condition_list: List[Condition]) -> None:
        """
        Adds multiple conditions to the ManyConditions object.

        Args:
            condition_list (List[Condition]): A list of conditions to be added.

        Raises:
            TypeError: If the condition_list argument is not a list.
            TypeError: If any of the conditions in the list are not Condition objects.
        """
        if not isinstance(condition_list, List):
            raise TypeError("condition_list must be a list")

        for condition in condition_list:
            if not isinstance(condition, Condition):
                raise TypeError("All elements of condition_list must be Condition objects.")
            self._condition_list.append(condition)


class AllConditions(ManyConditions):
    """
    A class that represents a collection of conditions where all conditions must be true to evaluate to true.

    Inherits from the ManyConditions abstract class.
    """
    def __init__(self, inverse: bool = False):
        """
        Initializes the AllConditions object.

        Args:
            inverse (bool, optional): Whether to invert the evaluation result. Defaults to False.
        """
        super().__init__(inverse)

    def compare(self) -> bool:
        """
        Compares all conditions in the list and returns True if all of them are true.

        Returns:
            bool: True if all conditions are true, False otherwise.
        """
        return all(self._condition_list)


class AnyConditions(ManyConditions):
    """
    A condition that is true if at least one of its child conditions is true.

    Inherits from the ManyConditions abstract class.
    """
    def __init__(self, inverse: bool = False) -> None:
        """
        Initializes an AnyConditions object.

        Parameters:
            inverse (bool): Whether the condition should be inverted. Defaults to False.
        """
        super().__init__(inverse)

    def compare(self) -> bool:
        """
        Returns True if at least one of the child conditions is True.

        Returns:
            bool: Whether at least one child condition is True.
        """
        return any(self._condition_list)


class NoneConditions(ManyConditions):
    """
    A class representing a condition that is true if none of its sub-conditions are true.
    
    Inherits from the ManyConditions abstract class.
    """
    def __init__(self, inverse: bool = False) -> None:
        """
        Initializes a new NoneConditions object.

        Args:
            inverse (bool): Whether to invert the condition result. Default is False.
        """
        super().__init__(inverse)

    def compare(self) -> bool:
        """
        Checks if none of the sub-conditions are true.

        Returns:
            bool: True if none of the sub-conditions are true, False otherwise.
        """
        return not any(self._condition_list)

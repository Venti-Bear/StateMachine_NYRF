from abc import ABC
import abc
import time
from types import NoneType
from typing import Callable, Optional, List, Any

from Partie1.condition import Condition
from Partie1.state import State
from state import State
from condition import Condition


class Transition(ABC):
    """Abstract base class for transitions between states.

    Attributes:
        __next_state (Optional[State]): The next state to transition to.

    Args:
        next_state (Optional[State], optional): The next state to transition to. Defaults to None.

    Raises:
        TypeError: If next_state is not of type State or NoneType.

    """

    __next_state: Optional[State]

    def __init__(self, next_state: Optional[State] = None) -> None:
        """Initializes a Transition object with the given next_state.

        Args:
            next_state (Optional[State], optional): The next state to transition to. Defaults to None.

        Raises:
            TypeError: If next_state is not of type State or NoneType.

        """

        if not isinstance(next_state, (State, NoneType)):
            raise TypeError('next_state must be of type State')

        self.__next_state = next_state

    @property
    def is_valid(self) -> bool:
        """Returns True if the next state is not None, False otherwise."""
        return self.__next_state is not None

    @property
    def next_state(self) -> Optional[State]:
        """Returns the next state to transition to."""
        return self.__next_state

    @next_state.setter
    def next_state(self, next_state: Optional[State]) -> None:
        """Sets the next state to transition to.

        Args:
            next_state (Optional[State]): The next state to transition to.
        """

        if not isinstance(next_state, (State, NoneType)):
            raise TypeError('next_state must be of type State')

        self.__next_state = next_state

    @property
    @abc.abstractmethod
    def is_transiting(self) -> bool:
        """Returns True if the transition conditions are met, False otherwise."""
        raise NotImplementedError

    def _exec_transiting_action(self) -> None:
        """Executes the do_transiting_action method."""
        self._do_transiting_action()

    def _do_transiting_action(self) -> None:
        """Performs the transiting action."""
        ...


class ConditionalTransition(Transition):
    """A transition that occurs conditionally based on a given `Condition` object.

    Attributes:
        __condition (Optional[Condition]): The condition that must be met for the transition to occur.
    """
    __condition: Optional[Condition]

    def __init__(self, next_state: Optional[State] = None, condition: Optional[Condition] = None) -> None:
        """
        Initializes a new `ConditionalTransition` object.

        Args:
            next_state (Optional[State], optional): The next state of the transition. Defaults to None.
            condition (Optional[Condition], optional): The condition that must be met for the transition to occur.
                Defaults to None. If no condition is provided, the transition will occur unconditionally.
        Raises:
            TypeError: If the condition is not an instance of `Condition` or `NoneType`.
        """
        super().__init__(next_state)

        if not isinstance(condition, (Condition, NoneType)):
            raise TypeError('condition must be of type Condition or None')

        self.__condition: Optional[Condition] = condition

    def is_valid(self) -> bool:
        """
        Returns True if the transition is valid.

        A `ConditionalTransition` object is considered valid if it has a next state and a condition.

        Returns:
            bool: True if the transition is valid, False otherwise.
        """
        return super().is_valid and self.__condition is not None

    @property
    def condition(self) -> Optional[Condition]:
        """
        Gets or sets the condition of the transition.

        If no condition is provided, the transition will occur unconditionally.

        Returns:
            Optional[Condition]: The condition that must be met for the transition to occur.
        Raises:
            TypeError: If the condition is not an instance of `Condition`.
        """
        return self.__condition

    @condition.setter
    def condition(self, condition: Optional[Condition]) -> None:
        """
        Sets the condition of the transition.

        Args:
            condition (Optional[Condition]): The condition that must be met for the transition to occur.
        Raises:
            TypeError: If the condition is not an instance of `Condition`.
        """
        if not isinstance(condition, Condition):
            raise TypeError("condition must be a Condition object or None")
        self.__condition = condition

    @property
    def is_transiting(self) -> bool:
        """
        Returns True if the transition is currently transiting.

        A `ConditionalTransition` is considered to be transiting if its condition is currently being met.

        Returns:
            bool: True if the transition is currently transiting, False otherwise.
        """
        return bool(self.__condition)


class ActionTransition(ConditionalTransition):
    """A conditional transition that triggers a list of actions upon transitioning.

    This class inherits from the ConditionalTransition class and adds a list of actions
    that are triggered when the transition condition is met.

    Attributes:
        __transiting_actions (list[Callable[[], None]]): A list of actions triggered upon transitioning.
    """
    __transiting_actions: list[Callable[[], None]]

    def __init__(self, next_state: Optional[State] = None, condition: Optional[Condition] = None) -> None:
        """
        Args:
            next_state (State, optional): The state to transition to. Defaults to None.
            condition (Condition, optional): The condition that must be met for the transition to occur.
                Defaults to None.
        """
        super().__init__(next_state, condition)
        self.__transiting_actions = []

    def _do_transiting_action(self) -> None:
        """Execute the transit actions for this transition."""
        for action in self.__transiting_actions:
            action()

    def add_transition_action(self, action: Callable[[], None]) -> None:
        """Add a callable object to the list of transit actions for this transition.

        Args:
            action: A callable object to be added to the list of transit actions.
            
        Raises:
            TypeError: If `action` is not a callable object.
        """
        if not isinstance(action, Callable):
            raise TypeError("action must be callable")

        self.__transiting_actions.append(action)


class MonitoredTransition(ActionTransition):
    """An ActionTransition with monitoring capabilities.

    This class extends the ActionTransition class with additional monitoring capabilities,
    such as transit count and last transit time.

    Attributes:
        custom_value (Any): A custom value that can be set and accessed at any time.
        __last_transit_time (float): The timestamp of the last transition.
        __transit_count (int): The number of times this transition has been executed.
    """
    custom_value: Any
    __last_transit_time: float
    __transit_count: int

    def __init__(self, next_state: Optional[State] = None, condition: Optional[Condition] = None) -> None:
        """
        Args:
            next_state (State, optional): The state to transition to. Defaults to None.
            condition (Condition, optional): The condition that must be met for the transition to occur.
                Defaults to None.
        """
        super().__init__(next_state, condition)
        self.__transit_count = 0
        self.__last_transit_time = 0.
        self.custom_value = None

    @property
    def transit_count(self) -> int:
        """The number of times this transition has been taken."""
        return self.__transit_count

    @property
    def last_transit_time(self) -> float:
        """The time at which this transition was last taken."""
        return self.__last_transit_time

    # todo this code is suspect
    def reset_transit_count(self) -> None:
        """Reset the transit count to zero."""
        self.__transit_count = 0

    def reset_last_transit_time(self) -> None:
        """Reset the last transit time to zero."""
        self.__last_transit_time = 0.

    def _exec_transiting_action(self) -> None:
        """Execute the transit actions for this transition and track the transit count and time."""
        self.__transit_count += 1
        self.__last_transit_time = time.perf_counter()
        return super()._exec_transiting_action()

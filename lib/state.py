from __future__ import annotations
from typing import Callable, Optional, List, TYPE_CHECKING, Any
import time

if TYPE_CHECKING:
    from transition import Transition


class Parameters:
    """
    Represents the parameters of a state in a state machine, such as whether it is a
    terminal state or whether to perform certain actions when entering or exiting the
    state. All parameters are set to False by default.

    Attributes:
        do_in_state_action_when_exiting (bool): A boolean indicating whether to perform
            in-state actions when exiting the state.
        do_in_state_action_when_entering (bool): A boolean indicating whether to
            perform in-state actions when entering the state.
        terminal (bool): A boolean indicating whether the state is a terminal state.
    """

    # do_in_state_action_when_exiting: bool
    # do_in_state_action_when_entering: bool
    # terminal: bool

    def __init__(self) -> None:
        self.terminal = False
        self.do_in_state_action_when_entering = False
        self.do_in_state_action_when_exiting = False


class State:
    """
    Represents a state in a state machine, including its transitions and associated
    actions.

    Attributes:
        __parameters (Parameters): The parameters of the state, such as whether it is a
            terminal state or whether to perform certain actions when entering or
            exiting the state.
        __transition (List[Transition]): The list of transitions available from the
            state.
    """
    # __parameters: Parameters
    # __transition: list['Transition']

    def __init__(self, parameters: Parameters = Parameters()) -> None:
        """
        Initializes a new instance of the State class with the given parameters.

        Args:
            parameters (Parameters, optional): The parameters of the state, such as
                whether it is a terminal state or whether to perform certain actions
                when entering or exiting the state. Defaults to Parameters().
        """
        
        if not isinstance(parameters, Parameters):
            raise TypeError("parameters must be a Parameters object")
        
        self.__transition = []
        self.__parameters = parameters

    def is_valid(self) -> bool:
        """
        Returns True if all transitions from the state are valid, False otherwise.
        """
        
        if len(self.__transition) == 0:
            return False

        return all((transition.is_valid for transition in self.__transition))

    @property
    def is_terminal(self) -> bool:
        """
        Returns True if the state is a terminal state, False otherwise.
        """
        
        return self.__parameters.terminal

    @property
    def is_transiting(self) -> Optional['Transition']:
        """
        Returns the first valid transition from the state that is currently transiting,
        or None if there is no such transition.
        """
        
        for transition in self.__transition:
            if transition.is_transiting:
                return transition

    def add_transition(self, transition: 'Transition') -> None:
        """
        Adds a new transition to the state.

        Args:
            transition (Transition): The transition to add.
        """
        from lib.transition import Transition
        if not isinstance(transition, Transition):
            raise TypeError("transition must be a Transition object")

        self.__transition.append(transition)

    def _exec_entering_action(self) -> None:
        """
        Executes the entering action of the state.
        """
        
        self._do_entering_action()

        if self.__parameters.do_in_state_action_when_entering:
            self._exec_in_state_action()

    def _exec_in_state_action(self) -> None:
        """
        Executes the in-state action of the state.
        """
        
        self._do_in_state_action()

    def _exec_exiting_action(self) -> None:
        """
        Executes the exiting action of the state.
        """
        
        if self.__parameters.do_in_state_action_when_exiting:
            self._exec_in_state_action()

        self._do_exiting_action()

    def _do_entering_action(self) -> None:
        """
        Performs the entering action of the state.
        """

    def _do_in_state_action(self) -> None:
        """
        Performs the in-state action of the state.
        """

    def _do_exiting_action(self) -> None:
        """
        Performs the exiting action of the state.
        """


    def __hash__(self) -> int:
        # not sure if this is needed:
        # https://stackoverflow.com/questions/11324271/what-is-the-default-hash-in-python#comment14907554_11324351
        return hash(id(self))


class ActionState(State):
    """
    Represents a state in a state machine that can perform actions when entering,
    within, or exiting the state, in addition to having transitions.

    Attributes:
        __entering_action (List[Callable[[], None]]): The list of actions to perform
            when entering the state.
        __in_state_action (List[Callable[[], None]]): The list of actions to perform
            while in the state.
        __exiting_action (List[Callable[[], None]]): The list of actions to perform
            when exiting the state.
    """

    def __init__(self, parameters: Parameters = Parameters()) -> None:
        """
        Initializes a new instance of the ActionState class with the given parameters.

        Args:
            parameters (Parameters, optional): The parameters of the state, such as
                whether it is a terminal state or whether to perform certain actions
                when entering or exiting the state. Defaults to Parameters().
        """
        
        super().__init__(parameters)
        self.__entering_action = []
        self.__in_state_action = []
        self.__exiting_action = []

    def _do_entering_action(self) -> None:
        """
        Performs all the entering actions associated with the state.
        """
        
        for entering_action in self.__entering_action:
            entering_action()

    def _do_in_state_action(self) -> None:
        """
        Performs all the in-state actions associated with the state.
        """
        
        for in_state_action in self.__in_state_action:
            in_state_action()

    def _do_exiting_action(self) -> None:
        """
        Performs all the exiting actions associated with the state.
        """
        
        for exiting_action in self.__exiting_action:
            exiting_action()

    def add_entering_action(self, action: Callable[[], None]) -> None:
        """
        Adds a new entering action to the state.

        Args:
            action (Callable[[], None]): The action to add.
        """
        
        if not isinstance(action, Callable):
            raise Exception("action must be callable.")
        else:
            self.__entering_action.append(action)

    def add_in_state_action(self, action: Callable[[], None]) -> None:
        """
        Adds a new in-state action to the state.

        Args:
            action (Callable[[], None]): The action to add.
        """
        
        if not isinstance(action, Callable):
            raise Exception("action must be callable.")
        else:
            self.__in_state_action.append(action)

    def add_exiting_action(self, action: Callable[[], None]) -> None:
        """
        Adds a new exiting action to the state.

        Args:
            action (Callable[[], None]): The action to add.
        """
        
        if not isinstance(action, Callable):
            raise Exception("action must be callable.")
        else:
            self.__exiting_action.append(action)



class MonitoredState(ActionState):
    """
    A state in a state machine that can be monitored to record metrics such as the
    number of times the state was entered, the time since the last entry or exit, and
    a custom value associated with the state.

    Attributes:
        custom_value (Any): A custom value associated with the state.
        __entry_count (int): The number of times the state was entered.
        __counter_last_exit (float): The time the state was last exited, in seconds.
        __counter_last_entry (float): The time the state was last entered, in seconds.
    """

    def __init__(self, parameters: Parameters = Parameters()) -> None:
        """
        Initializes a new instance of the MonitoredState class with the given parameters.

        Args:
            parameters (Parameters, optional): The parameters of the state, such as
                whether it is a terminal state or whether to perform certain actions
                when entering or exiting the state. Defaults to Parameters().
        """
        
        super().__init__(parameters)
        self.__counter_last_entry = 0.0
        self.__counter_last_exit = 0.0
        self.__entry_count = 0
        self.custom_value = None

    @property
    def entry_count(self) -> int:
        """
        The number of times the state was entered.
        """
        
        return self.__entry_count

    @property
    def last_entry_time(self) -> float:
        """
        The time, in seconds, since the last time the state was entered.
        """
        
        return self.__counter_last_entry

    @property
    def last_exit_time(self) -> float:
        """
        The time, in seconds, since the last time the state was exited.
        """
        
        return self.__counter_last_exit

    def reset_entry_count(self) -> None:
        """
        Resets the entry count for the state to zero.
        """
        
        self.__entry_count = 0

    def reset_last_times(self) -> None:
        """
        Resets the last entry and exit times for the state to zero.
        """
        
        self.__counter_last_entry, self.__counter_last_exit = 0.0, 0.0

    def _exec_entering_action(self) -> None:
        """
        Performs all the entering actions associated with the state and updates the
        monitored state properties.
        """
        
        self.__counter_last_entry = time.perf_counter()
        self.__entry_count += 1
        super()._exec_entering_action()

    def _exec_exiting_action(self) -> None:
        """
        Performs all the exiting actions associated with the state and updates the
        monitored state properties.
        """
        
        self.__counter_last_exit = time.perf_counter()
        super()._exec_exiting_action()

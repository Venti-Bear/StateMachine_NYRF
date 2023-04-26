from typing import Optional, Set
from state import State


class Layout:
    __states: set[State]
    __initial_state: Optional[State]

    def __init__(self) -> None:
        """
        Initializes a new instance of the Layout class with an empty set of states
        and no initial state.
        """

        self.__initial_state = None
        self.__states = set()

    def is_valid(self) -> bool:
        """
        Checks if the layout is valid by verifying that it has an initial state and 
        that all its states are valid.

        Returns:
            A boolean indicating if the layout is valid.
        """

        if self.initial_state is None:
            return False

        return all((state.is_valid for state in self.__states))

    def add_state(self, state: State) -> None:
        """
        Adds a new state to the layout.

        Args:
            state: A State object representing the new state to add.

        Raises:
            TypeError: If state is not of type State.
        """

        if not isinstance(state, State):
            raise TypeError('state must be of type State')

        self.__states.add(state)

    def add_states(self, states: Set[State]) -> None:
        """
        Adds multiple states to the layout.

        Args:
            states: A set of State objects representing the new states to add.

        Raises:
            TypeError: If any of the states is not of type State.
        """

        for state in states:
            if not isinstance(state, State):
                raise TypeError('state must be of type State')

        self.__states = self.__states.union(states)

    @property
    def initial_state(self) -> Optional[State]:
        """
        Gets the initial state of the layout.

        Returns:
            An Optional[State] representing the initial state of the layout, or None
            if no initial state has been set.
        """

        return self.__initial_state

    @initial_state.setter
    def initial_state(self, state) -> None:
        """
        Sets the initial state of the layout.

        Args:
            state: A State object representing the initial state.

        Raises:
            Exception: If the state is not part of the layout states.
        """

        if state not in self.__states:
            raise Exception(
                "the initial state must be part of the Layout states")
        self.__initial_state = state

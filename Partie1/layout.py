from typing import Optional, Set
from state import State


class Layout:
    def __init__(self) -> None:
        self.__initial_state: Optional[State] = None
        self.__states: Set[State] = set()

    def is_valid(self) -> bool:
        if self.initial_state is None:
            return False

        return all((state.is_valid() for state in self.__states))

    def add_state(self, state: State) -> None:
        self.__states.add(state)

    def add_states(self, states: Set[State]) -> None:
        self.__states = self.__states.union(states)

    @property
    def initial_state(self) -> Optional[State]:
        return self.__initial_state

    @initial_state.setter
    def initial_state(self, state) -> None:

        if state not in self.__states:
            raise Exception("the initial state must be part of the Layout states")
        self.__initial_state = state

from __future__ import annotations
from typing import Optional, List, TYPE_CHECKING

if TYPE_CHECKING:
    from transition import Transition


class Parameters:
    def __init__(self):
        self.terminal: bool = False
        self.do_in_state_action_when_entering: bool = False
        self.do_in_state_action_when_exiting: bool = False


class State:
    """todo"""

    def __init__(self, parameters: Optional[Parameters] = Parameters()):
        self.__transition: List[Transition] = []
        self.__parameters: Parameters = parameters

    @property
    def is_valid(self) -> bool:
        """todo"""
        if len(self.__transition) == 0:
            return False

        return all((transition.is_valid() for transition in self.__transition))

    @property
    def is_terminal(self) -> bool:
        """todo"""
        return self.__parameters.terminal

    @property
    def is_transiting(self):
        """todo"""
        for transition in self.__transition:
            if transition.is_transiting:
                return transition

    def add_transition(self, transition: Transition):
        """todo"""
        self.__transition.append(transition)

    def _exec_entering_action(self):
        """todo"""
        self._do_entering_action()

        if self.__parameters.do_in_state_action_when_entering:
            self._exec_in_state_action()

    def _exec_in_state_action(self):
        """todo"""
        self._do_in_state_action()

    def _exec_exiting_action(self):
        """todo"""
        if self.__parameters.do_in_state_action_when_exiting:
            self._exec_in_state_action()

        self._do_exiting_action()

    def _do_entering_action(self):
        """todo"""

    def _do_in_state_action(self):
        """todo"""

    def _do_exiting_action(self):
        """todo"""

    def __hash__(self):
        # not sure if this is needed:
        # https://stackoverflow.com/questions/11324271/what-is-the-default-hash-in-python#comment14907554_11324351
        return hash(id(self))

from enum import Enum, auto
from abc import ABC, abstractmethod
class FiniteStateMachine(ABC):
    pass

class State():
    @abstractmethod
    def get_transitions():
        pass

class Transition():
    def __init__(self, next_state):
        self.__next_state = next_state
        pass
    pass
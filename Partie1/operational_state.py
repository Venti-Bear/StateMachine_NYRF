from enum import Enum, auto


class OperationalState(Enum):
    UNINITIALIZED = auto()
    IDLE = auto()
    RUNNING = auto()
    TERMINAL_REACHED = auto()

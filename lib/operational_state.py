from enum import Enum, auto


class OperationalState(Enum):
    """
    Defines an enumeration of operational states that a system or process can be in.

    OperationalState is an enumeration class that defines four states: UNINITIALIZED,
    IDLE, RUNNING, and TERMINAL_REACHED. Each state is represented by a unique value
    that can be compared to other instances of the same class using equality operators.

    The values for each state are generated automatically using the `auto()` function
    from the `enum` module. This ensures that each state has a unique value that is
    not dependent on its position in the enumeration definition.

    Example usage:
        # Create an OperationalState instance
        state = OperationalState.IDLE

        # Compare two instances of the same class
        if state == OperationalState.RUNNING:
            print("The system is currently running.")

        # Loop through all states in the enumeration
        for state in OperationalState:
            print(state)
    """
    UNINITIALIZED = auto()
    IDLE = auto()
    RUNNING = auto()
    TERMINAL_REACHED = auto()

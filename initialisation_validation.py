from state import *
from layout import Layout
from transition import ConditionalTransition
from condition import StateEntryDurationCondition
from Robot import Robot

class InitializationValidation(Layout):
    def __init__(self):
        self.__robot = Robot()

        ROBOT_INSTANTIATION = MonitoredState()

        INSTANTIATION_FAILED = ActionState()
        INSTANTIATION_FAILED.add_in_state_action(lambda: (print("Robot is not connected")))

        ROBOT_INTEGRITY = MonitoredState()
        ROBOT_INTEGRITY.add_in_state_action(self.__robot.check_integrity)
        
        END = State(Parameters(False, True, True))


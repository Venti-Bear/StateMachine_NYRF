from state import *
from layout import Layout
from transition import ConditionalTransition
from condition import StateEntryDurationCondition, ValueCondition
from Robot import Robot
from blinker import Side

class InitializationValidation(Layout):
    def __init__(self):
        self.__robot = Robot()

        success = ValueCondition()

        ROBOT_INSTANTIATION = MonitoredState()
        ROBOT_INSTANTIATION.custom_value = self.__robot.is_instantiated

        INSTANTIATION_FAILED = ActionState()
        INSTANTIATION_FAILED.add_in_state_action(lambda: (print("Robot is not connected")))


        ROBOT_INTEGRITY = MonitoredState()
        ROBOT_INTEGRITY.custom_value = self.__robot.is_trustworthy      # has integrity
        
        END = ActionState(Parameters(False, True, True))
        END.add_in_state_action(lambda: (print("Robot shutting down")))
        
        INTEGRITY_FAILED = ActionState(Parameters(False, True, True))
        INTEGRITY_FAILED.add_in_state_action(lambda: (print('One or more components are not working')))
        INTEGRITY_FAILED.add_in_state_action(self.__robot.set_eye_color("red"))
        INTEGRITY_FAILED.add_in_state_action(self.__robot.blink(Side.BOTH, total_duration=5.0, cycle_duration=0.5, percent_on=0.5))

        INTEGRITY_SUCCEEDED = MonitoredState()
        INTEGRITY_SUCCEEDED.add_in_state_action(lambda: (print('Initialization successful, starting robot')))
        INTEGRITY_SUCCEEDED.add_in_state_action(self.__robot.set_eye_color("green"))
        INTEGRITY_SUCCEEDED.add_in_state_action(self.__robot.blink(Side.BOTH, total_duration=3.0, cycle_duration=1.0, percent_on=0.5))




from state import *
from layout import Layout
from transition import ConditionalTransition
from condition import StateEntryDurationCondition, StateValueCondition
from Robot import Robot
from blinker import Side

class InitializationValidation(Layout):
    def __init__(self):
        self.__robot = Robot()

        ROBOT_INSTANTIATION = MonitoredState()
        ROBOT_INSTANTIATION.custom_value = self.__robot.is_instantiated()

        INSTANTIATION_FAILED = ActionState()
        INSTANTIATION_FAILED.add_in_state_action(lambda: (print("Robot is not connected")))

        instantiation_success = StateValueCondition(True, ROBOT_INSTANTIATION)
        instantiation_fail = StateValueCondition(False, ROBOT_INSTANTIATION)
        ROBOT_INSTANTIATION_SUCC = ConditionalTransition(ROBOT_INTEGRITY, instantiation_success)
        ROBOT_INSTANTIATION_FAIL = ConditionalTransition(INSTANTIATION_FAILED, instantiation_fail)
        ROBOT_INSTANTIATION.add_transition(ROBOT_INSTANTIATION_SUCC)
        ROBOT_INSTANTIATION.add_transition(ROBOT_INSTANTIATION_FAIL)

        ROBOT_INTEGRITY = MonitoredState()
        ROBOT_INTEGRITY.custom_value = self.__robot.is_trustworthy      # has integrity
        
        INTEGRITY_FAILED = ActionState(Parameters(False, True, True))
        INTEGRITY_FAILED.add_in_state_action(lambda: (print('One or more components are not working')))
        INTEGRITY_FAILED.add_in_state_action(self.__robot.set_eye_color("red"))
        INTEGRITY_FAILED.add_in_state_action(self.__robot.blink(Side.BOTH, total_duration=5.0, cycle_duration=0.5, percent_on=0.5))

        INTEGRITY_SUCCEEDED = MonitoredState()
        INTEGRITY_SUCCEEDED.add_in_state_action(lambda: (print('Initialization successful, starting robot')))
        INTEGRITY_SUCCEEDED.add_in_state_action(self.__robot.set_eye_color("green"))
        INTEGRITY_SUCCEEDED.add_in_state_action(self.__robot.blink(Side.BOTH, total_duration=3.0, cycle_duration=1.0, percent_on=0.5))

        integrity_success = StateValueCondition(True, ROBOT_INTEGRITY)
        integrity_fail = StateValueCondition(False, ROBOT_INTEGRITY)
        ROBOT_INTEGRITY_SUCC = ConditionalTransition(INTEGRITY_SUCCEEDED, integrity_success)
        ROBOT_INTEGRITY_FAIL = ConditionalTransition(INTEGRITY_FAILED, integrity_fail)
        ROBOT_INTEGRITY.add_transition(ROBOT_INTEGRITY_SUCC)
        ROBOT_INTEGRITY.add_transition(ROBOT_INTEGRITY_FAIL)

        SHUT_DOWN_ROBOT = MonitoredState()
        SHUT_DOWN_ROBOT.add_in_state_action(lambda: (print("Shutting down, don't turn off your robot")))
        SHUT_DOWN_ROBOT.add_in_state_action(self.__robot.set_eye_color("yellow"))
        SHUT_DOWN_ROBOT.add_in_state_action(self.__robot.blink(Side.LEFT_RECIPROCAL, cycle_duration=0.75, percent_on=0.5))

        shut_down_condition = StateEntryDurationCondition(3.0, SHUT_DOWN_ROBOT)
        ROBOT_SHUT_DOWN_COMPLETE = ConditionalTransition(END, shut_down_condition)
        SHUT_DOWN_ROBOT.add_transition(ROBOT_SHUT_DOWN_COMPLETE)

        END = ActionState(Parameters(False, True, True))
        END.add_in_state_action(lambda: (print("You may now turn off your robot")))




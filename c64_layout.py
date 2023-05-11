from state import *
from robot_state import RobotState
from layout import Layout
from transition import ConditionalTransition
from condition import StateEntryDurationCondition, StateValueCondition
from Robot import Robot
from blinker import Side
from time import perf_counter

class C64Layout(Layout):
    def __init__(self):
        self.__robot = Robot()

        ### VERIFICATION DE L'INSTANTIATION ################################################
        ROBOT_INSTANTIATION = RobotState(self.__robot)
        ROBOT_INSTANTIATION.custom_value = self.__robot.initialize()

        # etat d'echec
        INSTANTIATION_FAILED = ActionState()
        INSTANTIATION_FAILED.add_in_state_action(lambda: (print("Robot is not connected")))

        ### VERIFICATION DE L'INTEGRITE ####################################################
        ROBOT_INTEGRITY = RobotState(self.__robot)
        ROBOT_INTEGRITY.custom_value = self.__robot.check_integrity()  # has integrity

        # Conditions et transitions
        instantiation_success = StateValueCondition(True, ROBOT_INSTANTIATION)
        instantiation_fail = StateValueCondition(False, ROBOT_INSTANTIATION)
        ROBOT_INSTANTIATION_SUCC = ConditionalTransition(ROBOT_INTEGRITY, instantiation_success)
        ROBOT_INSTANTIATION_FAIL = ConditionalTransition(INSTANTIATION_FAILED, instantiation_fail)
        ROBOT_INSTANTIATION.add_transition(ROBOT_INSTANTIATION_SUCC)
        ROBOT_INSTANTIATION.add_transition(ROBOT_INSTANTIATION_FAIL)

        # etat d'echec
        INTEGRITY_FAILED = ActionState(Parameters())
        INTEGRITY_FAILED.add_in_state_action(lambda: (print('\rOne or more components are not working', end=' ')))
        INTEGRITY_FAILED.add_entering_action(lambda: self.__robot.set_eye_color((100, 0, 0)))
        INTEGRITY_FAILED.add_entering_action(lambda: self.__robot.blink_eye(Side.BOTH, total_duration=5.0, cycle_duration=0.5, percent_on=0.5))

        # etat de succes
        INTEGRITY_SUCCEEDED = RobotState(self.__robot)
        INTEGRITY_SUCCEEDED.add_in_state_action(lambda: (print('\rInitialization successful, starting robot', perf_counter(), end=' ')))
        INTEGRITY_SUCCEEDED.add_entering_action(lambda: self.__robot.set_eye_color((0, 100, 0)))
        INTEGRITY_SUCCEEDED.add_entering_action(lambda: self.__robot.blink_eye(Side.BOTH, total_duration=3.0, cycle_duration=1.0, percent_on=0.5))

        # conditions et transitions
        integrity_success = StateValueCondition(True, ROBOT_INTEGRITY)
        integrity_fail = StateValueCondition(False, ROBOT_INTEGRITY)
        ROBOT_INTEGRITY_SUCC = ConditionalTransition(INTEGRITY_SUCCEEDED, integrity_success)
        ROBOT_INTEGRITY_FAIL = ConditionalTransition(INTEGRITY_FAILED, integrity_fail)
        ROBOT_INTEGRITY.add_transition(ROBOT_INTEGRITY_SUCC)
        ROBOT_INTEGRITY.add_transition(ROBOT_INTEGRITY_FAIL)

        ### SHUTDOWN DU ROBOT ##############################################################
        SHUT_DOWN_ROBOT = RobotState(self.__robot)
        SHUT_DOWN_ROBOT.add_in_state_action(lambda: (print("\rShutting down, don't turn off your robot", end=' ')))
        SHUT_DOWN_ROBOT.add_entering_action(lambda: self.__robot.set_eye_color((100, 100, 0)))
        SHUT_DOWN_ROBOT.add_entering_action(lambda: self.__robot.blink_eye(Side.LEFT_RECIPROCAL, cycle_duration=0.75, percent_on=0.5))

        # etat eteint
        END = ActionState(Parameters())
        END.add_in_state_action(lambda: (print("\rYou may now turn off your robot", end=' ')))

        # condition et transition
        shut_down_condition = StateEntryDurationCondition(3.0, SHUT_DOWN_ROBOT)
        ROBOT_SHUT_DOWN_COMPLETE = ConditionalTransition(END, shut_down_condition)
        SHUT_DOWN_ROBOT.add_transition(ROBOT_SHUT_DOWN_COMPLETE)

        ### GOING HOME #####################################################################
        HOME = RobotState(self.__robot)
        HOME.add_in_state_action(lambda: self.__robot.set_eye_color((100, 100, 0)))
        HOME.add_in_state_action(lambda: self.__robot.blink_eye(Side.RIGHT_RECIPROCAL, cycle_duration=1.5, percent_on=0.5))

        # condition et transition pour se rendre a Home
        integrity_to_home = StateEntryDurationCondition(3.0, INTEGRITY_SUCCEEDED)
        ROBOT_SUCCEED_TO_HOME = ConditionalTransition(HOME, integrity_to_home)
        INTEGRITY_SUCCEEDED.add_transition(ROBOT_SUCCEED_TO_HOME)

        self.add_states({ROBOT_INSTANTIATION, INSTANTIATION_FAILED, ROBOT_INTEGRITY, END, INTEGRITY_FAILED, INTEGRITY_SUCCEEDED, HOME})
        self.initial_state = ROBOT_INSTANTIATION




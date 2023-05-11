from state import *
from layout import Layout
from transition import ConditionalTransition
from condition import StateEntryDurationCondition, StateValueCondition
from Robot import Robot
from blinker import Side

class C64Layout(Layout):
    def __init__(self, exiting_state):
        self.__robot = Robot()

        ### VERIFICATION DE L'INSTANTIATION ################################################
        ROBOT_INSTANTIATION = MonitoredState()
        ROBOT_INSTANTIATION.custom_value = self.__robot.is_instantiated()

        # etat d'echec
        INSTANTIATION_FAILED = ActionState()
        INSTANTIATION_FAILED.add_in_state_action(lambda: (print("Robot is not connected")))

        # Conditions et transitions
        instantiation_success = StateValueCondition(True, ROBOT_INSTANTIATION)
        instantiation_fail = StateValueCondition(False, ROBOT_INSTANTIATION)
        ROBOT_INSTANTIATION_SUCC = ConditionalTransition(ROBOT_INTEGRITY, instantiation_success)
        ROBOT_INSTANTIATION_FAIL = ConditionalTransition(INSTANTIATION_FAILED, instantiation_fail)
        ROBOT_INSTANTIATION.add_transition(ROBOT_INSTANTIATION_SUCC)
        ROBOT_INSTANTIATION.add_transition(ROBOT_INSTANTIATION_FAIL)

        ### VERIFICATION DE L'INTEGRITE ####################################################
        ROBOT_INTEGRITY = MonitoredState()
        ROBOT_INTEGRITY.custom_value = self.__robot.is_trustworthy      # has integrity
        
        # etat d'echec
        INTEGRITY_FAILED = ActionState(Parameters(False, True, True))
        INTEGRITY_FAILED.add_in_state_action(lambda: (print('One or more components are not working')))
        INTEGRITY_FAILED.add_in_state_action(lambda: self.__robot.set_eye_color((100, 0, 0)))
        INTEGRITY_FAILED.add_in_state_action(lambda: self.__robot.blink(Side.BOTH, total_duration=5.0, cycle_duration=0.5, percent_on=0.5))

        # etat de succes
        INTEGRITY_SUCCEEDED = MonitoredState()
        INTEGRITY_SUCCEEDED.add_in_state_action(lambda: (print('Initialization successful, starting robot')))
        INTEGRITY_SUCCEEDED.add_in_state_action(self.__robot.set_eye_color("green"))
        INTEGRITY_SUCCEEDED.add_in_state_action(self.__robot.blink(Side.BOTH, total_duration=3.0, cycle_duration=1.0, percent_on=0.5))

        # conditions et transitions
        integrity_success = StateValueCondition(True, ROBOT_INTEGRITY)
        integrity_fail = StateValueCondition(False, ROBOT_INTEGRITY)
        ROBOT_INTEGRITY_SUCC = ConditionalTransition(INTEGRITY_SUCCEEDED, integrity_success)
        ROBOT_INTEGRITY_FAIL = ConditionalTransition(INTEGRITY_FAILED, integrity_fail)
        ROBOT_INTEGRITY.add_transition(ROBOT_INTEGRITY_SUCC)
        ROBOT_INTEGRITY.add_transition(ROBOT_INTEGRITY_FAIL)

        ### SHUTDOWN DU ROBOT ##############################################################
        SHUT_DOWN_ROBOT = MonitoredState()
        SHUT_DOWN_ROBOT.add_in_state_action(lambda: (print("Shutting down, don't turn off your robot")))
        SHUT_DOWN_ROBOT.add_in_state_action(self.__robot.set_eye_color("yellow"))
        SHUT_DOWN_ROBOT.add_in_state_action(self.__robot.blink(Side.LEFT_RECIPROCAL, cycle_duration=0.75, percent_on=0.5))

        # etat eteint
        END = ActionState(Parameters(False, True, True))
        END.add_in_state_action(lambda: (print("You may now turn off your robot")))

        # condition et transition
        shut_down_condition = StateEntryDurationCondition(3.0, SHUT_DOWN_ROBOT)
        ROBOT_SHUT_DOWN_COMPLETE = ConditionalTransition(END, shut_down_condition)
        SHUT_DOWN_ROBOT.add_transition(ROBOT_SHUT_DOWN_COMPLETE)

        ### GOING HOME #####################################################################
        HOME = MonitoredState()
        HOME.add_in_state_action(self.__robot.set_eye_color("yellow"))
        HOME.add_in_state_action(self.__robot.blink(Side.RIGHT_RECIPROCAL, cycle_duration=1.5, percent_on=0.5))

        # condition et transition pour se rendre a Home
        integrity_to_home = StateEntryDurationCondition(3.0, INTEGRITY_SUCCEEDED)
        ROBOT_SUCCEED_TO_HOME = ConditionalTransition(HOME, integrity_to_home)
        INTEGRITY_SUCCEEDED.add_transition(ROBOT_SUCCEED_TO_HOME)

        self.add_states({ROBOT_INSTANTIATION, INSTANTIATION_FAILED, ROBOT_INTEGRITY, END, INTEGRITY_FAILED, INTEGRITY_SUCCEEDED})
        self.initial_state = ROBOT_INSTANTIATION

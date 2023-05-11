from state import *
from robot_state import RobotState
from layout import Layout
from transition import ConditionalTransition, ActionTransition
from condition import StateEntryDurationCondition, Condition, StateValueCondition, AlwaysTrueCondition
from Robot import Robot
from blinker import Side
from Task01_manual_control import ManualControlState

class C64Layout(Layout):
    def __init__(self):
        self.__robot = Robot()

        # etat d'echec
        INSTANTIATION_FAILED = ActionState()
        INSTANTIATION_FAILED.add_entering_action(lambda: (print("Robot is not connected")))

        ### VERIFICATION DE L'INSTANTIATION ################################################
        ROBOT_INSTANTIATION = RobotState(self.__robot)
        ROBOT_INSTANTIATION.custom_value = self.__robot.initialize()

        ### VERIFICATION DE L'INTEGRITE ####################################################
        ROBOT_INTEGRITY = RobotState(self.__robot)

        def check_integrity():
            ROBOT_INTEGRITY.custom_value = self.__robot.check_integrity()

        ROBOT_INTEGRITY.add_entering_action(check_integrity)

        # Conditions et transitions
        instantiation_success = StateValueCondition(True, ROBOT_INSTANTIATION)
        instantiation_fail = StateValueCondition(False, ROBOT_INSTANTIATION)
        ROBOT_INSTANTIATION_SUCC = ConditionalTransition(ROBOT_INTEGRITY, instantiation_success)
        ROBOT_INSTANTIATION_FAIL = ConditionalTransition(INSTANTIATION_FAILED, instantiation_fail)
        ROBOT_INSTANTIATION.add_transition(ROBOT_INSTANTIATION_SUCC)
        ROBOT_INSTANTIATION.add_transition(ROBOT_INSTANTIATION_FAIL)

        # etat d'echec
        INTEGRITY_FAILED = RobotState(self.__robot)
        INTEGRITY_FAILED.add_entering_action(lambda: (print('One or more components are not working')))
        INTEGRITY_FAILED.add_entering_action(lambda: self.__robot.set_eye_color((50, 0, 0)))
        INTEGRITY_FAILED.add_entering_action(lambda: self.__robot.blink_eye(Side.BOTH, total_duration=5.0, cycle_duration=0.5, percent_on=0.5))

        # etat de succes
        INTEGRITY_SUCCEEDED = RobotState(self.__robot)
        INTEGRITY_SUCCEEDED.add_entering_action(lambda: (print('Initialization successful, starting robot')))
        INTEGRITY_SUCCEEDED.add_entering_action(lambda: self.__robot.set_eye_color((0, 50, 0)))
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
        SHUT_DOWN_ROBOT.add_entering_action(lambda: (print("Shutting down, don't turn off your robot")))
        SHUT_DOWN_ROBOT.add_entering_action(lambda: self.__robot.set_eye_color((50, 50, 0)))
        SHUT_DOWN_ROBOT.add_entering_action(lambda: self.__robot.blink_eye(Side.LEFT_RECIPROCAL, cycle_duration=0.75, percent_on=0.5))
        SHUT_DOWN_ROBOT.add_exiting_action(lambda: self.__robot.shut_down())

        condition = StateEntryDurationCondition(5.0, INTEGRITY_FAILED)
        transition = ConditionalTransition(SHUT_DOWN_ROBOT, condition)
        INTEGRITY_FAILED.add_transition(transition)

        # etat eteint
        param = Parameters()
        param.terminal = True
        END = ActionState(param)
        END.add_entering_action(lambda: (print("You may now turn off your robot")))

        transition = ConditionalTransition(END, AlwaysTrueCondition())
        INSTANTIATION_FAILED.add_transition(transition)

        # condition et transition
        shut_down_condition = StateEntryDurationCondition(3.0, SHUT_DOWN_ROBOT)
        ROBOT_SHUT_DOWN_COMPLETE = ConditionalTransition(END, shut_down_condition)
        SHUT_DOWN_ROBOT.add_transition(ROBOT_SHUT_DOWN_COMPLETE)

        # TASK_1
        task_1 = ManualControlState(self.__robot)

        taches = [
            task_1
        ]

        ### GOING HOME #####################################################################
        HOME = RobotState(self.__robot)
        HOME.add_entering_action(lambda: self.__robot.set_eye_color((50, 50, 0)))
        HOME.add_entering_action(lambda: (print('Welcome home!')))
        HOME.add_entering_action(lambda: self.__robot.blink_eye(Side.RIGHT_RECIPROCAL, cycle_duration=1.5, percent_on=0.5))

        condition = StateEntryDurationCondition(2.0, HOME)
        cond_transition = ConditionalTransition(task_1, condition)
        #HOME.add_transition(cond_transition)

        for i, tache in enumerate(taches):
            cond = ControllerCondition(self.__robot, str(i + 1))
            transition = ActionTransition(tache, cond)
            transition.add_transition_action(self.__robot.controller_clear_buffer)

            HOME.add_transition(transition)

            cond = ControllerCondition(self.__robot, None)
            transition = ActionTransition(HOME, cond)
            transition.add_transition_action(self.__robot.controller_clear_buffer)
            tache.add_transition(transition)

        cond = ControllerCondition(self.__robot, None)
        transition = ActionTransition(HOME, cond)
        transition.add_transition_action(self.__robot.controller_clear_buffer)
        HOME.add_transition(transition)

        # condition et transition pour se rendre a Home
        integrity_to_home = StateEntryDurationCondition(3.0, INTEGRITY_SUCCEEDED)
        ROBOT_SUCCEED_TO_HOME = ConditionalTransition(HOME, integrity_to_home)
        INTEGRITY_SUCCEEDED.add_transition(ROBOT_SUCCEED_TO_HOME)

        super().__init__()

        self.add_states({ROBOT_INSTANTIATION, INSTANTIATION_FAILED, ROBOT_INTEGRITY, END, INTEGRITY_FAILED, INTEGRITY_SUCCEEDED, HOME})
        self.initial_state = ROBOT_INSTANTIATION


class ControllerCondition(Condition):
    def __init__(self, robot: Robot, texte: Optional[str], inverse: bool = False) -> None:
        self.robot = robot
        self.texte = texte
        super().__init__(inverse)

    def compare(self) -> bool:
        if self.robot.controller_peek_last_char() == "ok":
            #print("is none?", self.robot.controller_peek_last_char())
            buffer = self.robot.controller_buffer[:-1]
            #print(buffer)
            if self.texte is None:
                print(self.texte is None)
                return True
            else:
                if ''.join(buffer) == self.texte:
                    self.robot.controller_clear_buffer()
                    return True
                else:
                    return False
        else:
            return False


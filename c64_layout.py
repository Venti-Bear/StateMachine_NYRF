from Task02_crash_avoidance import CrashAvoidanceState
from lib.state import *
from robot_state import RobotState
from lib.layout import Layout
from lib.transition import ConditionalTransition, ActionTransition
from lib.condition import StateEntryDurationCondition, Condition, StateValueCondition, AlwaysTrueCondition
from Robot import Robot
from lib.blinker import Side
from Task01_manual_control import ManualControlState

class C64Layout(Layout):
    def __init__(self):
        self.__robot = Robot()

        # etat d'echec
        instantiation_failed = ActionState()
        instantiation_failed.add_entering_action(lambda: (print("Robot is not connected")))

        ### VERIFICATION DE L'INSTANTIATION ################################################
        robot_instantiation = RobotState(self.__robot)
        robot_instantiation.custom_value = self.__robot.initialize()

        ### VERIFICATION DE L'INTEGRITE ####################################################
        robot_integrity = RobotState(self.__robot)

        def check_integrity():
            robot_integrity.custom_value = self.__robot.check_integrity()

        robot_integrity.add_entering_action(check_integrity)

        # Conditions et transitions
        instantiation_success = StateValueCondition(True, robot_instantiation)
        instantiation_fail = StateValueCondition(False, robot_instantiation)
        robot_instantiation_succ = ConditionalTransition(robot_integrity, instantiation_success)
        robot_instantiation_fail = ConditionalTransition(instantiation_failed, instantiation_fail)
        robot_instantiation.add_transition(robot_instantiation_succ)
        robot_instantiation.add_transition(robot_instantiation_fail)

        # etat d'echec
        integrity_failed = RobotState(self.__robot)
        integrity_failed.add_entering_action(lambda: (print('One or more components are not working')))
        integrity_failed.add_entering_action(lambda: self.__robot.set_eye_color((255, 0, 0)))
        integrity_failed.add_entering_action(lambda: self.__robot.blink_eye(Side.BOTH, total_duration=5.0, cycle_duration=0.5, percent_on=0.5))

        # etat de succes
        integrity_succeeded = RobotState(self.__robot)
        integrity_succeeded.add_entering_action(lambda: (print('Initialization successful, starting robot')))
        integrity_succeeded.add_entering_action(lambda: self.__robot.set_eye_color((0, 50, 0)))
        integrity_succeeded.add_entering_action(lambda: self.__robot.blink_eye(Side.BOTH, total_duration=3.0, cycle_duration=1.0, percent_on=0.5))

        # conditions et transitions
        integrity_success = StateValueCondition(True, robot_integrity)
        integrity_fail = StateValueCondition(False, robot_integrity)
        robot_integrity_succ = ConditionalTransition(integrity_succeeded, integrity_success)
        robot_integrity_fail = ConditionalTransition(integrity_failed, integrity_fail)
        robot_integrity.add_transition(robot_integrity_succ)
        robot_integrity.add_transition(robot_integrity_fail)

        ### SHUTDOWN DU ROBOT ##############################################################
        shut_down_robot = RobotState(self.__robot)
        shut_down_robot.add_entering_action(lambda: (print("Shutting down, don't turn off your robot")))
        shut_down_robot.add_entering_action(lambda: self.__robot.set_eye_color((50, 40, 0)))
        shut_down_robot.add_entering_action(lambda: self.__robot.blink_eye(Side.LEFT_RECIPROCAL, cycle_duration=0.75, percent_on=0.5))
        shut_down_robot.add_exiting_action(lambda: self.__robot.shut_down())

        condition = StateEntryDurationCondition(5.0, integrity_failed)
        transition = ConditionalTransition(shut_down_robot, condition)
        integrity_failed.add_transition(transition)

        # etat eteint
        param = Parameters()
        param.terminal = True
        end = ActionState(param)
        end.add_entering_action(lambda: (print("You may now turn off your robot")))

        transition = ConditionalTransition(end, AlwaysTrueCondition())
        instantiation_failed.add_transition(transition)

        # condition et transition
        shut_down_condition = StateEntryDurationCondition(3.0, shut_down_robot)
        robot_shut_down_complete = ConditionalTransition(end, shut_down_condition)
        shut_down_robot.add_transition(robot_shut_down_complete)

        taches = [
            # TASK 1
            ManualControlState(self.__robot),

            # TASK 2
            CrashAvoidanceState(self.__robot)
        ]

        ### GOING HOME #####################################################################
        home = RobotState(self.__robot)
        home.add_entering_action(lambda: self.__robot.set_eye_color((50, 40, 0)))
        home.add_entering_action(lambda: (print('Welcome home!')))
        home.add_entering_action(lambda: self.__robot.blink_eye(Side.RIGHT_RECIPROCAL, cycle_duration=1.5, percent_on=0.5))

        condition = StateEntryDurationCondition(2.0, home)

        for i, tache in enumerate(taches):
            cond = ControllerCondition(self.__robot, str(i + 1))
            transition = ActionTransition(tache, cond)
            transition.add_transition_action(self.__robot.controller_clear_buffer)

            home.add_transition(transition)

            cond = ControllerCondition(self.__robot, None)
            transition = ActionTransition(home, cond)
            transition.add_transition_action(self.__robot.controller_clear_buffer)
            tache.add_transition(transition)

        cond = ControllerCondition(self.__robot, "#")
        transition = ActionTransition(shut_down_robot, cond)
        transition.add_transition_action(self.__robot.controller_clear_buffer)
        home.add_transition(transition)

        cond = ControllerCondition(self.__robot, None)
        transition = ActionTransition(home, cond)
        transition.add_transition_action(self.__robot.controller_clear_buffer)
        home.add_transition(transition)


        # condition et transition pour se rendre a Home
        integrity_to_home = StateEntryDurationCondition(3.0, integrity_succeeded)
        robot_succeed_to_home = ConditionalTransition(home, integrity_to_home)
        integrity_succeeded.add_transition(robot_succeed_to_home)

        super().__init__()

        self.add_states({robot_instantiation, instantiation_failed, robot_integrity, end, integrity_failed, integrity_succeeded, home})
        self.initial_state = robot_instantiation


class ControllerCondition(Condition):
    def __init__(self, robot: Robot, texte: Optional[str], inverse: bool = False) -> None:
        self.__robot = robot
        self.__texte = texte
        super().__init__(inverse)

    def compare(self) -> bool:
        if self.__robot.controller_peek_last_char() == "ok":
            buffer = self.__robot.controller_buffer[:-1]
            if self.__texte is None:
                print(self.__texte is None)
                return True
            else:
                if ''.join(buffer) == self.__texte:
                    self.__robot.controller_clear_buffer()
                    return True
                else:
                    return False
        else:
            return False


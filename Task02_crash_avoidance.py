from lib.blinker import Side
from lib.state import MonitoredState
from lib.transition import ConditionalTransition
from lib.condition import StateValueCondition, StateEntryDurationCondition
from lib.finite_state_machine import FiniteStateMachine
from robot_state import RobotState
from lib.layout import Layout
from Robot import Robot, Direction


class CrashAvoidanceState(RobotState):

    def __init__(self, robot: Robot):
        self.__robot = robot
        super().__init__(robot)
        self.__crash_avoidance = CrashAvoidance(robot)
        self.add_in_state_action(lambda: self.__crash_avoidance.track())
        self.add_exiting_action(self.STOP)

    def STOP(self):
        self.__robot.direction = None


class CrashAvoidance(FiniteStateMachine):
    __THRESHOLD_CM = 30

    def __init__(self, robot: Robot):
        self.__initialize = False
        self.robot = robot
        peek_right_state, peek_left_state, forward_state, rotate_right_state = [
            MonitoredState() for _ in range(4)]

        def forward():
            robot.movement_direction = Direction.FORWARD

        def rotate_right():
            robot.movement_direction = Direction.RIGHT

        def peek_right():
            robot.range_finder_angle = 50

        def peek_left():
            robot.range_finder_angle = -50

        def peek_forward():
            robot.range_finder_angle = 0

        peek_left_state.add_in_state_action(peek_left)
        peek_right_state.add_in_state_action(peek_right)

        cond = StateEntryDurationCondition(3.0, peek_left_state)
        transition = ConditionalTransition(peek_right_state, cond)
        peek_left_state.add_transition(transition)

        cond = StateEntryDurationCondition(3.0, peek_right_state)
        transition = ConditionalTransition(forward_state, cond)
        peek_right_state.add_transition(transition)

        forward_state.add_in_state_action(forward)
        forward_state.add_in_state_action(peek_forward)
        rotate_right_state.add_in_state_action(rotate_right)
        rotate_right_state.add_in_state_action(peek_forward)

        rotate_right_state.add_entering_action(
            lambda: self.robot.turn_eye_on(Side.BOTH))
        rotate_right_state.add_exiting_action(
            lambda: self.robot.turn_eye_off(Side.BOTH))

        in_range_cond = StateValueCondition(False, forward_state)
        out_of_range_cond = StateValueCondition(True, rotate_right_state)

        transiton = ConditionalTransition(forward_state, out_of_range_cond)
        rotate_right_state.add_transition(transiton)

        transiton = ConditionalTransition(rotate_right_state, in_range_cond)
        forward_state.add_transition(transiton)

        self.__layout = Layout()
        self.__layout.add_states(
            {forward_state, rotate_right_state, peek_left_state, peek_right_state})
        self.__layout.initial_state = peek_left_state

        super().__init__(self.__layout, uninitialized=True)

    def track(self):
        if not self.__initialize:
            self.reset()
            self.__initialize = True
        self.current_applicative_state.custom_value = self.robot.distance_cm >= CrashAvoidance.__THRESHOLD_CM
        super().track()

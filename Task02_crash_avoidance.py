from lib.blinker import Side
from lib.state import MonitoredState
from lib.transition import ConditionalTransition
from lib.condition import StateValueCondition
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
    __TRESHOLD_CM = 30

    def __init__(self, robot: Robot):
        self.robot = robot
        forward_state, rotate_right_state = [MonitoredState() for _ in range(2)]

        def forward():
            robot.movement_direction = Direction.FORWARD

        def rotate_right():
            robot.movement_direction = Direction.RIGHT

        forward_state.add_in_state_action(forward)
        rotate_right_state.add_in_state_action(rotate_right)

        rotate_right_state.add_entering_action(lambda: self.robot.turn_eye_on(Side.BOTH))
        rotate_right_state.add_exiting_action(lambda: self.robot.turn_eye_off(Side.BOTH))


        in_range_cond = StateValueCondition(False, forward_state)
        out_of_range_cond = StateValueCondition(True, rotate_right_state)

        transiton = ConditionalTransition(forward_state, out_of_range_cond)
        rotate_right_state.add_transition(transiton)

        transiton = ConditionalTransition(rotate_right_state, in_range_cond)
        forward_state.add_transition(transiton)

        self.__layout = Layout()
        self.__layout.add_states(
            {forward_state, rotate_right_state})
        self.__layout.initial_state = forward_state

        super().__init__(self.__layout, uninitialized=False)

    def track(self):
        self.current_applicative_state.custom_value = self.robot.distance_cm >= CrashAvoidance.__TRESHOLD_CM

        super().track()
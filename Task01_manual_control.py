from lib.blinker import Side
from lib.state import MonitoredState
from lib.transition import ConditionalTransition
from lib.condition import StateValueCondition
from lib.finite_state_machine import FiniteStateMachine
from robot_state import RobotState
from lib.layout import Layout
from Robot import Robot, Direction


class ManualControlState(RobotState):
    def __stop(self):
        self.__robot.direction = None

    def __init__(self, robot: Robot):
        super().__init__(robot)
        self.__robot = robot
        self.__manual_control = ManualControl(robot)
        self.add_in_state_action(lambda: self.__manual_control.track())
        self.add_exiting_action(self.__stop)


class ManualControl(FiniteStateMachine):
    def __init__(self, robot: Robot):
        self.robot = robot
        forward_state, backward_state, rotate_left_state, rotate_right_state, stop_state = [
            MonitoredState() for _ in range(5)]

        left_condition, not_left_condition = StateValueCondition(
            'left', stop_state), StateValueCondition('left', rotate_left_state, inverse=True)
        left, not_left = ConditionalTransition(
            rotate_left_state, left_condition), ConditionalTransition(stop_state, not_left_condition)

        rotate_left_state.add_transition(
            not_left), stop_state.add_transition(left)

        right_condition, not_right_condition = StateValueCondition(
            'right', stop_state), StateValueCondition('right', rotate_right_state, inverse=True)
        right, not_right = ConditionalTransition(
            rotate_right_state, right_condition), ConditionalTransition(stop_state, not_right_condition)

        rotate_right_state.add_transition(
            not_right), stop_state.add_transition(right)

        down_condition, not_down_condition = StateValueCondition(
            'down', stop_state), StateValueCondition('down', backward_state, inverse=True)
        down, not_down = ConditionalTransition(
            backward_state, down_condition), ConditionalTransition(stop_state, not_down_condition)

        backward_state.add_transition(
            not_down), stop_state.add_transition(down)

        up_condition, not_up_condition = StateValueCondition(
            'up', stop_state), StateValueCondition('up', forward_state, inverse=True)
        up, not_up = ConditionalTransition(
            forward_state, up_condition), ConditionalTransition(stop_state, not_up_condition)

        forward_state.add_transition(not_up), stop_state.add_transition(up)

        def forward():
            robot.movement_direction = Direction.FORWARD

        def backward():
            robot.movement_direction = Direction.BACKWARD

        def rotate_right():
            robot.movement_direction = Direction.RIGHT

        def rotate_left():
            robot.movement_direction = Direction.LEFT

        def stop():
            robot.movement_direction = None

        forward_state.add_in_state_action(forward)
        forward_state.add_entering_action(lambda: robot.blink_led(
            Side.BOTH, cycle_duration=1.0, percent_on=0.25, begin_on=True, end_off=False))
        backward_state.add_in_state_action(backward)
        backward_state.add_entering_action(lambda: robot.blink_led(
            Side.BOTH, cycle_duration=1.0, percent_on=0.75, begin_on=True, end_off=False))
        rotate_right_state.add_in_state_action(rotate_right)
        rotate_right_state.add_entering_action(lambda: robot.blink_led(
            Side.RIGHT, cycle_duration=1.0, percent_on=0.50, begin_on=True, end_off=False))
        rotate_left_state.add_in_state_action(rotate_left)
        rotate_left_state.add_entering_action(lambda: robot.blink_led(
            Side.LEFT, cycle_duration=1.0, percent_on=0.50, begin_on=True, end_off=False))
        stop_state.add_in_state_action(stop)
        stop_state.add_entering_action(
            lambda: robot.turn_led_off(side=Side.BOTH))

        self.__layout = Layout()
        self.__layout.add_states(
            {forward_state, backward_state, rotate_left_state, rotate_right_state, stop_state})
        self.__layout.initial_state = stop_state

        super().__init__(self.__layout, uninitialized=False)

    def track(self):
        self.current_applicative_state.custom_value = self.robot.controller_current_char()
        super().track()

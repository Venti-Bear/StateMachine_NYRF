from transition import ConditionalTransition
from condition import StateValueCondition
from finite_state_machine import FiniteStateMachine
from robot_state import RobotState
from layout import Layout
from Robot import Robot, Direction

class ManualControlState(RobotState):
    def STOP(self):
        self.robot.direction = None
        

    def __init__(self, robot: Robot):
        super().__init__(robot)
        self.robot = robot
        self.__manual_control = ManualControl(robot)
        # self.add_entering_action()            # À revoir, quitte à demander à J-C.
        self.add_in_state_action(lambda: self.__manual_control.track())
        self.add_exiting_action(self.STOP)

class ManualControl(FiniteStateMachine):
    def __init__(self, robot: Robot):
        self.robot = robot
        FORWARD, BACKWARD, ROTATE_LEFT, ROTATE_RIGHT, STOP = RobotState(self.robot), RobotState(self.robot), RobotState(self.robot), RobotState(self.robot), RobotState(self.robot)
        
        right_condition, not_right_condition = StateValueCondition('right', STOP), StateValueCondition('right', ROTATE_RIGHT, inverse=True)
        left_condition, not_left_condition = StateValueCondition('left', STOP), StateValueCondition('left', ROTATE_LEFT, inverse=True)
        up_condition, not_up_condition = StateValueCondition('up', STOP), StateValueCondition('up', FORWARD, inverse=True)
        down_condition, not_down_condition = StateValueCondition('down', STOP), StateValueCondition('down', BACKWARD, inverse=True)

        right, not_right = ConditionalTransition(ROTATE_RIGHT, right_condition), ConditionalTransition(STOP, not_right_condition)
        left, not_left = ConditionalTransition(ROTATE_LEFT, left_condition), ConditionalTransition(STOP, not_left_condition)
        up, not_up = ConditionalTransition(FORWARD, up_condition), ConditionalTransition(STOP, not_up_condition)
        down, not_down = ConditionalTransition(BACKWARD, down_condition), ConditionalTransition(STOP, not_down_condition)

        FORWARD.add_transition(not_up), STOP.add_transition(up)
        BACKWARD.add_transition(not_down), STOP.add_transition(down)
        ROTATE_RIGHT.add_transition(not_right), STOP.add_transition(right)
        ROTATE_LEFT.add_transition(not_left), STOP.add_transition(left)

        def forward():
            robot.movement_direction = Direction.FORWARD

        def backward():
            robot.movement_direction = Direction.BACKWARD

        def right():
            robot.movement_direction = Direction.RIGHT

        def left():
            robot.movement_direction = Direction.LEFT

        def stop():
            robot.movement_direction = None

        FORWARD.add_in_state_action(forward)
        BACKWARD.add_in_state_action(backward)
        ROTATE_RIGHT.add_in_state_action(right)
        ROTATE_LEFT.add_in_state_action(left)
        STOP.add_in_state_action(stop)
        
        self.__layout = Layout()
        self.__layout.add_states({ FORWARD, BACKWARD, ROTATE_LEFT, ROTATE_RIGHT, STOP })
        self.__layout.initial_state = STOP

        super().__init__(self.__layout, uninitialized=False)

    def track(self):
        self.current_applicative_state.custom_value = self.robot.controller_current_char()

        super().track()
from transition import ConditionalTransition
from condition import StateValueCondition
from finite_state_machine import FiniteStateMachine
from robot_state import RobotState
from layout import Layout
from Robot import Robot

class ManualControlState(RobotState):
    def __init__(self, robot: Robot):
        super.__init__(robot)
        self.__manual_control = ManualControl(robot)
        # self.add_entering_action()            # À revoir, quitte à demander à J-C.
        self.add_in_state_action(self.__manual_control.track)

class ManualControl(FiniteStateMachine):
    def __init__(self, robot: Robot):
        FORWARD, BACKWARD, ROTATE_LEFT, ROTATE_RIGHT, STOP = RobotState(robot), RobotState(robot), RobotState(robot), RobotState(robot), RobotState(robot)
        
        right_condition, not_right_condition = StateValueCondition('right', STOP), StateValueCondition('', ROTATE_RIGHT)
        left_condition, not_left_condition = StateValueCondition('left', STOP), StateValueCondition('', ROTATE_LEFT)
        up_condition, not_up_condition = StateValueCondition('up', STOP), StateValueCondition('', FORWARD)
        down_condition, not_down_condition = StateValueCondition('down', STOP), StateValueCondition('', BACKWARD)

        right, not_right = ConditionalTransition(ROTATE_RIGHT, right_condition), ConditionalTransition(STOP, not_right_condition)
        left, not_left = ConditionalTransition(ROTATE_LEFT, left_condition), ConditionalTransition(STOP, not_left_condition)
        up, not_up = ConditionalTransition(FORWARD, up_condition), ConditionalTransition(STOP, not_up_condition)
        down, not_down = ConditionalTransition(BACKWARD, down_condition), ConditionalTransition(STOP, not_down_condition)

        FORWARD.add_transition(not_up), STOP.add_transition(up)
        BACKWARD.add_transition(not_down), STOP.add_transition(down)
        ROTATE_RIGHT.add_transition(not_right), STOP.add_transition(right)
        ROTATE_LEFT.add_transition(not_left), STOP.add_transition(left)

        FORWARD.add_in_state_action(lambda: robot.forward)
        BACKWARD.add_in_state_action(lambda: robot.backward)
        ROTATE_RIGHT.add_in_state_action(lambda: robot.right)
        ROTATE_LEFT.add_in_state_action(lambda: robot.left)
        STOP.add_in_state_action(lambda: robot.stop)

        self.__layout = Layout()
        self.__layout.add_states({ FORWARD, BACKWARD, ROTATE_LEFT, ROTATE_RIGHT, STOP })
        self.__layout.initial_state = STOP

        super.__init__(self.__layout)
from state import MonitoredState
from Robot import Robot


class RobotState(MonitoredState):
    def __init__(self, robot: Robot):
        super().__init__()
        self.add_in_state_action(lambda: robot.track())
        self.add_entering_action(lambda: robot.reset_actuator())

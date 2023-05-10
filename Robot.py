# INITIALISATION ET VALIDATION
# ============================
# ROBOT_INSTANTIATION -> ROBOT_INTEGRITY if successful else INSTANTIATION_FAILED -> END
# ROBOT_INTEGRITY -> INTEGRITY SUCCEEDED if successful else INTEGRITY_FAILED -> SHUT_DOWN_ROBOT -> END
# INTEGRITY_SUCCEEDED -> HOME 

# ACCUEIL
# ============================
# HOME - TACHES (TASK_1, TASK_2, TASK_3, ...)

# TACHE
# ============================
# TASK_1 -> HOME
# TASK_2 -> HOME
# ...

# from GoPiGo3 import GoPiGo3
from enum import Enum, auto
from typing import Optional, Tuple

from blinker import SideBlinkers
from state import MonitoredState


class GoPiGo3:
    ...


class LedBlinkers(SideBlinkers):
    def __init__(self, robot: GoPiGo3):
        self.robot = robot

        def generate_off_state_left() -> MonitoredState:
            mon = MonitoredState()
            mon.add_entering_action(lambda: print('led_off_state_left'))
            return mon

        def generate_off_state_right() -> MonitoredState:
            mon = MonitoredState()
            mon.add_entering_action(lambda: print('led_off_state_right'))
            return mon

        def generate_on_state_left() -> MonitoredState:
            mon = MonitoredState()
            mon.add_entering_action(lambda: print('led_on_state_left'))
            return mon

        def generate_on_state_right() -> MonitoredState:
            mon = MonitoredState()
            mon.add_entering_action(lambda: print('led_on_state_right'))
            return mon

        super().__init__(generate_off_state_left, generate_on_state_left, generate_off_state_right,
                         generate_on_state_right)


class EyeBlinkers(SideBlinkers):
    def __init__(self, robot: GoPiGo3):
        self.robot = robot
        self.__right_color = (255, 255, 255)
        self.__left_color = (255, 255, 255)

        def generate_off_state_left() -> MonitoredState:
            mon = MonitoredState()
            mon.add_entering_action(lambda: self.robot.open_left_eye())
            mon.add_in_state_action(lambda: self.robot.set_left_eye_color(self.left_color))
            return mon

        def generate_off_state_right() -> MonitoredState:
            mon = MonitoredState()
            mon.add_entering_action(lambda: print('eye_off_state_right'))
            return mon

        def generate_on_state_left() -> MonitoredState:
            mon = MonitoredState()
            mon.add_entering_action(lambda: print('eye_on_state_left'))
            return mon

        def generate_on_state_right() -> MonitoredState:
            mon = MonitoredState()
            mon.add_entering_action(lambda: print('eye_on_state_right'))
            return mon

        super().__init__(generate_off_state_left, generate_on_state_left, generate_off_state_right,
                         generate_on_state_right)

    @property
    def right_color(self):
        return self.__right_color

    @right_color.setter
    def right_color(self, color: Tuple[int, int, int]):
        self.right_color = color

    @property
    def left_color(self):
        return self.__right_color

    @left_color.setter
    def left_color(self, color: Tuple[int, int, int]):
        self.right_color = color

    def set_color(self, color: Tuple[int, int, int]):
        self.left_color = color
        self.right_color = color


class Controller:
    def __init__(self, robot: GoPiGo3):
        self.robot = robot
        remote_control_port = 'AD1'
        self.remote_control = robot.init_remote(port=remote_control_port)
        self.keycode = ['', 'up', 'left', 'ok', 'right', 'down', '1', '2', '3', '4', '5', '6', '7', '8', '9', '*', '0', '#']
        self.last_char = ''
        self.input_buffer = []

    def track(self):
        char_num: int = self.remote.read()
        char = self.keycode[char_num]
        if char != "" and char != self.last_char:
            self.input_buffer.append(char)
        self.last_char = char

    def clear_buffer(self):
        self.input_buffer = []

    def next_char(self) -> Optional[str]:
        if not self.input_buffer:
            return None

        return self.input_buffer.pop()


class Direction(Enum):
    LEFT = auto()
    RIGHT = auto()
    FORWARD = auto()
    BACKWARD = auto()

    def __str__(self):
        return self.name


class Motor:
    def __init__(self, robot: GoPiGo3):
        self.robot = robot
        self.__current_direction = None

    @property
    def direction(self):
        return self.__current_direction

    @direction.setter
    def direction(self, direction: Optional[Direction]):
        self.__current_direction = direction
        if direction == Direction.FORWARD:
            self.__go_forward()
        elif direction == Direction.BACKWARD:
            self.__go_backward()
        elif direction == Direction.LEFT:
            self.__turn_left()
        elif direction == Direction.RIGHT:
            self.__turn_right()
        else:
            self.__stop()

    def __go_forward(self):
        self.robot.forward()

    def __go_backward(self):
        self.robot.backward()

    def __stop(self):
        self.robot.stop()

    def __turn_right(self):
        self.robot.right()

    def __turn_left(self):
        self.robot.left()


class Robot:
    def __init__(self):
        self.robot = GoPiGo3()
        self.led_blinkers = LedBlinkers(self.robot)
        self.eye_blinkers = EyeBlinkers(self.robot)
        self.motor = Motor(self.robot)
        self.controller = Controller(self.robot)

    def track(self) -> None:
        self.controller.track()
        self.eye_blinkers.track()
        self.led_blinkers.track()


c = Controller(GoPiGo3())
print(c.next_char())

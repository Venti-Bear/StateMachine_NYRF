from easygopigo3 import EasyGoPiGo3 as GoPiGo3
from enum import Enum, auto
from typing import Optional, Tuple, Union, List
from time import perf_counter

from lib.blinker import SideBlinkers, Side
from lib.state import MonitoredState


class LedBlinkers(SideBlinkers):
    def __init__(self, robot: GoPiGo3):
        self.robot = robot

        def generate_off_state_left() -> MonitoredState:
            mon = MonitoredState()
            mon.add_entering_action(lambda: self.robot.led_off('left'))
            return mon

        def generate_off_state_right() -> MonitoredState:
            mon = MonitoredState()
            mon.add_entering_action(lambda: self.robot.led_off('right'))
            return mon

        def generate_on_state_left() -> MonitoredState:
            mon = MonitoredState()
            mon.add_entering_action(lambda: self.robot.led_on('left'))
            return mon

        def generate_on_state_right() -> MonitoredState:
            mon = MonitoredState()            
            mon.add_entering_action(lambda: self.robot.led_on('right'))
            return mon

        super().__init__(generate_off_state_left, generate_on_state_left, generate_off_state_right,
                         generate_on_state_right)


class EyeBlinkers(SideBlinkers):
    def __init__(self, robot: GoPiGo3):
        self.robot = robot
        self.__right_color = (100, 100, 100)
        self.__left_color = (100, 100, 100)

        def generate_off_state_left() -> MonitoredState:
            mon = MonitoredState()
            mon.add_entering_action(lambda: self.robot.close_left_eye())
            return mon

        def generate_off_state_right() -> MonitoredState:
            mon = MonitoredState()
            mon.add_entering_action(lambda: self.robot.close_right_eye())
            return mon

        def generate_on_state_left() -> MonitoredState:
            mon = MonitoredState()
            mon.add_in_state_action(lambda: self.robot.open_left_eye())
            mon.add_in_state_action(lambda: self.robot.set_left_eye_color(self.left_color))
            return mon

        def generate_on_state_right() -> MonitoredState:
            mon = MonitoredState()
            mon.add_in_state_action(lambda: self.robot.open_right_eye())
            mon.add_in_state_action(lambda: self.robot.set_right_eye_color(self.right_color))
            return mon

        super().__init__(generate_off_state_left, generate_on_state_left, generate_off_state_right,
                         generate_on_state_right)

    @property
    def right_color(self):
        return self.__right_color

    @right_color.setter
    def right_color(self, color: Tuple[int, int, int]):
        self.__right_color = color

    @property
    def left_color(self):
        return self.__right_color

    @left_color.setter
    def left_color(self, color: Tuple[int, int, int]):
        self.__left_color = color

    def set_color(self, color: Tuple[int, int, int]):
        self.left_color = color
        self.right_color = color


class Controller:
    def __init__(self, robot: GoPiGo3):
        self.robot = robot
        remote_control_port = 'AD1'
        self.remote = robot.init_remote(port=remote_control_port)
        self.keycode = ['', 'up', 'left', 'ok', 'right', 'down', '1', '2', '3', '4', '5', '6', '7', '8', '9', '*', '0',
                        '#']
        self.last_char = ''
        self.__input_buffer = []

    @property
    def buffer(self):
        return self.__input_buffer[:]  # retourne une copie du buffer pour empecher les modifications accidentelles

    def track(self):
        char_num: int = self.remote.read()
        char = self.keycode[char_num]
        if char != "" and char != self.last_char:
            self.__input_buffer.append(char)
        self.last_char = char

    def clear_buffer(self):
        self.__input_buffer = []

    def next_char(self) -> Optional[str]:
        if not self.__input_buffer:
            return None

        return self.__input_buffer.pop(0)

    def peek_last_char(self) -> Optional[str]:
        if not self.__input_buffer:
            return None

        return self.__input_buffer[-1]

    def peek_char(self) -> Optional[str]:
        if not self.__input_buffer:
            return None

        return self.__input_buffer[0]

    def current_char(self) -> Optional[str]:
        if self.last_char == self.peek_last_char():
            return self.last_char
        return None

    def check_integrity(self):
        return self.robot is not None


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
            self.robot.forward()
        elif direction == Direction.BACKWARD:
            self.robot.backward()
        elif direction == Direction.LEFT:
            self.robot.left()
        elif direction == Direction.RIGHT:
            self.robot.right()
        else:
            self.robot.stop()


class RangeFinder:
    def __init__(self, robot: GoPiGo3):
        self.robot = robot
        self.sensor = self.robot.init_distance_sensor()
        self.servo = self.robot.init_servo(port='SERVO2')

    @property
    def distance_mm(self):
        dist = self.sensor.read_mm()
        if dist > 2300:
            return None
        return dist

    @property
    def distance_cm(self):
        dist = self.sensor.read()
        if dist > 230:
            return None
        return dist

    def check_integrity(self):
        return self.sensor is not None


class Robot:
    def __init__(self):
        self.robot = None
        self.led_blinkers = None
        self.eye_blinkers = None
        self.motor = None
        self.controller = None
        self.range_finder = None
        self.__integrity = False

    def track(self) -> None:
        if self.__integrity:
            self.controller.track()
        self.eye_blinkers.track()
        self.led_blinkers.track()

    def initialize(self):
        try:
            if self.robot is None:
                self.robot = GoPiGo3()

                if self.robot is not None:
                    self.led_blinkers = LedBlinkers(self.robot)
                    self.eye_blinkers = EyeBlinkers(self.robot)
                    self.motor = Motor(self.robot)
                    self.reset_actuator()
                    return True
                else:
                    return False
        except:
            return False

    def check_integrity(self):
        try:
            if self.controller is None:
                self.controller = Controller(self.robot)

            if self.range_finder is None:
                self.range_finder = RangeFinder(self.robot)

            self.__integrity = self.range_finder.check_integrity() and self.controller.check_integrity()
            return self.__integrity
        except:
            return False

    def set_eye_color(self, color: Tuple):
        self.eye_blinkers.set_color(color)

    @property
    def left_eye_color(self):
        return self.eye_blinkers.left_color

    @left_eye_color.setter
    def left_eye_color(self, color: Tuple[int, int, int]):
        self.eye_blinkers.left_color = color

    @property
    def right_eye_color(self):
        return self.eye_blinkers.right_color

    @right_eye_color.setter
    def right_eye_color(self, color: Tuple[int, int, int]):
        self.eye_blinkers.right_color = color

    @property
    def distance_mm(self):
        return self.range_finder.distance_mm

    @property
    def distance_cm(self):
        result = self.range_finder.distance_cm
        if result is not None:
            return result
        else:
            return 3000


    def get_next_controller_input(self):
        return self.controller.next_char()

    def clear_controller_buffer(self):
        self.controller.clear_buffer()

    def is_eye_on(self, side: Side) -> bool:
        return self.eye_blinkers.is_on(side)

    def is_led_on(self, side: Side) -> bool:
        return self.led_blinkers.is_on(side)

    def is_eye_off(self, side: Side) -> bool:
        return self.eye_blinkers.is_off(side)

    def is_led_off(self, side: Side) -> bool:
        return self.led_blinkers.is_off(side)

    def turn_eye_on(self, side: Side, duration: Optional[Union[float, int]] = None) -> None:
        self.eye_blinkers.turn_on(side, duration)

    def turn_eye_off(self, side: Side, duration: Optional[Union[float, int]] = None) -> None:
        self.eye_blinkers.turn_off(side, duration)

    def turn_led_on(self, side: Side, duration: Optional[Union[float, int]] = None) -> None:
        self.led_blinkers.turn_on(side, duration)

    def turn_led_off(self, side: Side, duration: Optional[Union[float, int]] = None) -> None:
        self.led_blinkers.turn_off(side, duration)

    def blink_eye(self, side: Side, *, total_duration: Optional[Union[float, int]] = None,
                  cycle_duration: Optional[Union[float, int]] = None, n_cycles: Optional[int] = None,
                  percent_on: Union[float, int] = 0.5, begin_on: bool = True, end_off: bool = True) -> None:

        self.eye_blinkers.blink(side, total_duration=total_duration, cycle_duration=cycle_duration, n_cycles=n_cycles, percent_on=percent_on, begin_on=begin_on, end_off=end_off)

    def blink_led(self, side: Side, *, total_duration: Optional[Union[float, int]] = None,
                  cycle_duration: Optional[Union[float, int]] = None, n_cycles: Optional[int] = None,
                  percent_on: Union[float, int] = 0.5, begin_on: bool = True, end_off: bool = True) -> None:

        self.led_blinkers.blink(side, total_duration=total_duration, cycle_duration=cycle_duration, n_cycles=n_cycles, percent_on=percent_on, begin_on=begin_on, end_off=end_off)

    @property
    def movement_direction(self):
        return self.motor.direction

    @movement_direction.setter
    def movement_direction(self, direction: Direction):
        self.motor.direction = direction

    def shut_down(self):
        self.reset_actuator()
        self.controller = None
        self.range_finder = None
        # On "éteint" le robot
        del self 

    @property
    def controller_buffer(self) -> List:
        return self.controller.buffer

    def controller_clear_buffer(self) -> None:
        self.controller.clear_buffer()

    def controller_next_char(self) -> Optional[str]:
        return self.controller.next_char()

    def controller_peek_last_char(self) -> Optional[str]:
        return self.controller.peek_last_char()

    def controller_peek_char(self) -> Optional[str]:
        return self.controller.peek_char()
    
    def controller_current_char(self) -> Optional[str]:
        return self.controller.current_char()

    def reset_actuator(self):
        self.motor.direction = None
        self.turn_eye_off(Side.BOTH)
        self.turn_led_off(Side.BOTH)
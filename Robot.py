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
from typing import Optional

from blinker import SideBlinkers
from state import MonitoredState


class GoPiGo3:
    ...


class LedBlinkers(SideBlinkers):
    def __init__(self, robot: ...):
        self.robot = robot

        def generate_off_state_left():
            mon = MonitoredState()
            mon.add_entering_action(lambda: print('led_off_state_left'))
            return mon

        def generate_off_state_right():
            mon = MonitoredState()
            mon.add_entering_action(lambda: print('led_off_state_right'))
            return mon

        def generate_on_state_left():
            mon = MonitoredState()
            mon.add_entering_action(lambda: print('led_on_state_left'))
            return mon

        def generate_on_state_right():
            mon = MonitoredState()
            mon.add_entering_action(lambda: print('led_on_state_right'))
            return mon

        super().__init__(generate_off_state_left, generate_on_state_left, generate_off_state_right,
                         generate_on_state_right)


class EyeBlinkers(SideBlinkers):
    def __init__(self, robot: GoPiGo3):
        self.robot = robot

        def generate_off_state_left():
            mon = MonitoredState()
            mon.add_entering_action(lambda: print('eye_off_state_left'))
            return mon

        def generate_off_state_right():
            mon = MonitoredState()
            mon.add_entering_action(lambda: print('eye_off_state_right'))
            return mon

        def generate_on_state_left():
            mon = MonitoredState()
            mon.add_entering_action(lambda: print('eye_on_state_left'))
            return mon

        def generate_on_state_right():
            mon = MonitoredState()
            mon.add_entering_action(lambda: print('eye_on_state_right'))
            return mon

        super().__init__(generate_off_state_left, generate_on_state_left, generate_off_state_right,
                         generate_on_state_right)


class Controller:
    def __init__(self, robot: GoPiGo3):
        self.robot = robot
        # remote_control_port = 'AD1'
        # self.remote_control = robot.init_remote(port=remote_control_port)
        self.keycode = ['', 'up', 'left', 'ok', 'right', 'down', '1', '2', '3', '4', '5', '6', '7', '8', '9', '*', '0', '#']
        self.last_char = ''
        self.input_buffer = []

    def poll_remote(self):
        char_num: int = self.remote.read()
        char = self.keycode[char_num]
        if char != "" and char != self.last_char:
            self.input_buffer.append(char)
        self.last_char = char

    def clear_buffer(self):
        self.input_buffer = []

    def next_char(self) -> Optional[str]:
        char = None
        return self.input_buffer.pop()


class Robot:
    def __init__(self):
        self.robot = ...
        self.led_blinkers = ...  # LedBlinkers(self.robot)
        self.eye_blinkers = ...  # EyeBlinkers(self.robot)


c = Controller(GoPiGo3())
print(c.next_char())

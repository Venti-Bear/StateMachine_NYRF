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
from typing import Callable

from blinker import SideBlinkers
from state import MonitoredState


class EyeBlinkers(SideBlinkers):
    def __init__(self, robot: ...):

        def generate_off_state_left():
            return MonitoredState()

        def generate_off_state_right():
            return MonitoredState()

        def generate_on_state_left():
            return MonitoredState()

        def generate_on_state_right():
            return MonitoredState()

        super().__init__(generate_off_state_left, generate_on_state_left, generate_off_state_right,
                         generate_on_state_right)


class Robot:
    def __init__(self):
        self.robot = ...
        self.led_blinkers = ...  # LedBlinkers(self.robot)
        self.eye_blinkers = ...  # EyeBlinkers(self.robot)



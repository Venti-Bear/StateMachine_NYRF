from state import *
from layout import Layout
from transition import ConditionalTransition
from condition import StateEntryDurationCondition
from Robot import Robot
from blinker import Side

class InitializationValidation(Layout):
    def __init__(self):
        self.__robot = Robot()

        ROBOT_INSTANTIATION = MonitoredState()

        INSTANTIATION_FAILED = ActionState()
        INSTANTIATION_FAILED.add_in_state_action(lambda: (print("Robot is not connected")))

        INSTANTIATION_SUCCEEDED = ActionState()
        INSTANTIATION_SUCCEEDED.add_in_state_action(lambda: (print("Robot is connected")))

        ROBOT_INTEGRITY = MonitoredState()
        ROBOT_INTEGRITY.add_in_state_action(self.__robot.check_integrity)
        
        param = Parameters()
        param.terminal = False
        param.do_in_state_action_when_entering = True
        param.do_in_state_action_when_exiting = True

        END = ActionState(param)
        END.add_in_state_action(lambda: (print("Robot shutting down")))
        
        INTEGRITY_FAILED = ActionState(param)
        INTEGRITY_FAILED.add_in_state_action(lambda: (print('One or more components are not working')))
        INTEGRITY_FAILED.add_in_state_action(lambda: self.__robot.set_eye_color((100, 0, 0)))
        INTEGRITY_FAILED.add_in_state_action(lambda: self.__robot.blink(Side.BOTH, total_duration=5.0, cycle_duration=0.5, percent_on=0.5))

        INTEGRITY_SUCCEEDED = MonitoredState()
        INTEGRITY_SUCCEEDED.add_in_state_action(lambda: (print('Initialization successful, starting robot')))
        INTEGRITY_SUCCEEDED.add_in_state_action(lambda: self.__robot.set_eye_color((0, 100, 0)))
        INTEGRITY_SUCCEEDED.add_in_state_action(lambda: self.__robot.blink(Side.BOTH, total_duration=3.0, cycle_duration=1.0, percent_on=0.5))
        
        super().__init__()

        self.add_states({ROBOT_INSTANTIATION, INSTANTIATION_FAILED, INSTANTIATION_SUCCEEDED, ROBOT_INTEGRITY, END, INTEGRITY_FAILED, INTEGRITY_SUCCEEDED})
        self.initial_state = ROBOT_INSTANTIATION

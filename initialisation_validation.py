from state import *
from layout import Layout
from transition import ConditionalTransition
from condition import StateEntryDurationCondition
from Robot import Robot
from blinker import Side

class InitializationValidation(Layout):
    def __init__(self):
        self.__robot = Robot()

        robot_instantiation = MonitoredState()

        instantiation_failed = ActionState()
        instantiation_failed.add_in_state_action(lambda: (print("Robot is not connected")))

        instantiation_succeeded = ActionState()
        instantiation_succeeded.add_in_state_action(lambda: (print("Robot is connected")))

        robot_integrity = MonitoredState()
        robot_integrity.add_in_state_action(self.__robot.check_integrity)
        
        param = Parameters()
        param.terminal = False
        param.do_in_state_action_when_entering = True
        param.do_in_state_action_when_exiting = True

        END = ActionState(param)
        END.add_in_state_action(lambda: (print("Robot shutting down")))
        
        integrity_failed = ActionState(param)
        integrity_failed.add_in_state_action(lambda: (print('One or more components are not working')))
        integrity_failed.add_in_state_action(lambda: self.__robot.set_eye_color((100, 0, 0)))
        integrity_failed.add_in_state_action(lambda: self.__robot.blink(Side.BOTH, total_duration=5.0, cycle_duration=0.5, percent_on=0.5))

        integrity_succeeded = MonitoredState()
        integrity_succeeded.add_in_state_action(lambda: (print('Initialization successful, starting robot')))
        integrity_succeeded.add_in_state_action(lambda: self.__robot.set_eye_color((0, 100, 0)))
        integrity_succeeded.add_in_state_action(lambda: self.__robot.blink(Side.BOTH, total_duration=3.0, cycle_duration=1.0, percent_on=0.5))
        
        super().__init__()

        self.add_states({robot_instantiation, instantiation_failed, instantiation_succeeded, robot_integrity, END, integrity_failed, integrity_succeeded})
        self.initial_state = robot_instantiation

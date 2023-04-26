from finite_state_machine import FiniteStateMachine
from layout import Layout
from state import MonitoredState
from transition import ConditionalTransition
from condition import StateValueCondition, StateEntryDurationCondition

from typing import Callable, Optional, Union


class Blinker(FiniteStateMachine):
    __blink_on_cond: StateEntryDurationCondition
    __blink_stop_on_cond: StateEntryDurationCondition
    __blink_off_cond: StateEntryDurationCondition
    __on_duration_cond: StateEntryDurationCondition
    __off_duration_cond: StateEntryDurationCondition
    __blink_stop_end: MonitoredState
    __blink_stop_begin: MonitoredState
    __blink_begin: MonitoredState
    __on_duration: MonitoredState
    __off_duration: MonitoredState
    __on: MonitoredState
    __off: MonitoredState

    def __init__(self, off_state_generator: Callable[[], MonitoredState],
                 on_state_generator: Callable[[], MonitoredState]) -> None:
        layout = Layout()

        self.__off = off_state_generator()
        self.__on = on_state_generator()

        self.__off_duration = off_state_generator()
        self.__on_duration = on_state_generator()

        self.__blink_begin = MonitoredState()
        blink_off = off_state_generator()
        blink_on = on_state_generator()

        self.__blink_stop_begin = MonitoredState()
        self.__blink_stop_end = MonitoredState()

        blink_stop_on = on_state_generator()
        blink_stop_off = off_state_generator()

        # transition #

        # off/on duration
        self.__off_duration_cond = StateEntryDurationCondition(0, self.__off_duration)
        self.__on_duration_cond = StateEntryDurationCondition(0, self.__on_duration)

        self.__off_duration.add_transition(ConditionalTransition(self.__on, self.__off_duration_cond))
        self.__on_duration.add_transition(ConditionalTransition(self.__off, self.__on_duration_cond))

        # blink off/on
        self.__blink_off_cond = StateEntryDurationCondition(0, blink_off)
        self.__blink_on_cond = StateEntryDurationCondition(0, blink_on)

        blink_off.add_transition(ConditionalTransition(blink_on, self.__blink_off_cond))
        blink_on.add_transition(ConditionalTransition(blink_off, self.__blink_on_cond))

        cond_off = StateValueCondition("off", self.__blink_begin)
        cond_on = StateValueCondition("on", self.__blink_begin)

        self.__blink_begin.add_transition(ConditionalTransition(blink_on, cond_on))
        self.__blink_begin.add_transition(ConditionalTransition(blink_off, cond_off))

        # stop

        self.__blink_stop_off_cond = StateEntryDurationCondition(0, blink_stop_off)
        self.__blink_stop_on_cond = StateEntryDurationCondition(0, blink_stop_on)

        blink_stop_off.add_transition(ConditionalTransition(blink_stop_on, self.__blink_stop_off_cond))
        blink_stop_on.add_transition(ConditionalTransition(blink_stop_off, self.__blink_stop_on_cond))

        cond_off = StateValueCondition("off", self.__blink_stop_begin)
        cond_on = StateValueCondition("on", self.__blink_stop_begin)

        self.__blink_stop_begin.add_transition(ConditionalTransition(blink_stop_on, cond_on))
        self.__blink_stop_begin.add_transition(ConditionalTransition(blink_stop_off, cond_off))

        self.__blink_stop_cond = StateEntryDurationCondition(0, self.__blink_stop_begin)
        transition = ConditionalTransition(self.__blink_stop_end, self.__blink_stop_cond)

        blink_stop_off.add_transition(transition)
        blink_stop_on.add_transition(transition)

        # add to layout

        layout.add_states(
            {self.__off, self.__on, self.__off_duration, self.__on_duration, blink_off, blink_on, blink_stop_off,
             blink_stop_on, self.__blink_begin, self.__blink_stop_begin, self.__blink_stop_end})

        layout.initial_state = self.__off

        super().__init__(layout)

    def turn_on(self, duration: Optional[Union[float, int]] = None) -> None:
        if not isinstance(duration, (float, int)) and duration is not None:
            raise TypeError("duration must be a float, a int or None")

        if duration is None:
            self.transit_to(self.__on)
        else:
            self.__on_duration_cond.duration = duration
            self.transit_to(self.__on_duration)

    def turn_off(self, duration: Optional[Union[float, int]] = None) -> None:
        if not isinstance(duration, (float, int)) and duration is not None:
            raise TypeError("duration must be a float, a int or None")

        if duration is None:
            self.transit_to(self.__off)
        else:
            self.__off_duration_cond.duration = duration
            self.transit_to(self.__off_duration)

    def blink(self, *, total_duration: Optional[Union[float, int]] = None,
              cycle_duration: Optional[Union[float, int]] = None, n_cycles: Optional[int] = None,
              percent_on: Union[float, int] = 0.5, begin_on: bool = True, end_off: bool = True) -> None:

        if not isinstance(total_duration, (float, int)) and total_duration is not None:
            raise TypeError("total_duration must be a float, a int or None")
        elif not isinstance(cycle_duration, (float, int)) and cycle_duration is not None:
            raise TypeError("cycle_duration must be a float, a int or None")
        elif not isinstance(n_cycles, int):
            raise TypeError("n_cycles must be a int")
        elif not isinstance(percent_on, (int, float)):
            raise TypeError("percent_on must be a float or a int")
        elif not isinstance(begin_on, bool):
            raise TypeError("begin_on must be a bool")
        elif not isinstance(end_off, bool):
            raise TypeError("end_off must be a bool")
        elif not (0 <= percent_on <= 1):
            raise ValueError("percent_on must be between 0 and 1")

        if cycle_duration is not None and total_duration is None and n_cycles is None:
            self.__blink(cycle_duration, percent_on, begin_on)
        elif total_duration is not None and cycle_duration is not None and n_cycles is None:
            self.__blink_stop(total_duration, cycle_duration, percent_on, begin_on, end_off)
        elif total_duration is not None and cycle_duration is None and n_cycles is not None:
            cycle_duration = total_duration / n_cycles
            self.__blink_stop(total_duration, cycle_duration, percent_on, begin_on, end_off)
        elif total_duration is None and cycle_duration is not None and n_cycles is not None:
            total_duration = cycle_duration * n_cycles
            self.__blink_stop(total_duration, cycle_duration, percent_on, begin_on, end_off)
        else:
            raise TypeError("invalid calling convention")

    def __blink(self, cycle_duration: Union[float, int], percent_on: Union[float, int], begin_on: bool) -> None:
        on_time = cycle_duration * percent_on
        off_time = cycle_duration - on_time

        self.__blink_begin.custom_value = "on" if begin_on else "off"
        self.__blink_on_cond.duration = on_time
        self.__blink_off_cond.duration = off_time

        self.transit_to(self.__blink_begin)

    def __blink_stop(self, total_duration: Union[float, int], cycle_duration: Union[float, int],
                     percent_on: Union[float, int], begin_on: bool, end_off: bool) -> None:
        on_time = cycle_duration * percent_on
        off_time = cycle_duration - on_time

        self.__blink_stop_cond.duration = total_duration

        self.__blink_on_cond.duration = on_time
        self.__blink_off_cond.duration = off_time

        self.__blink_stop_begin.custom_value = "on" if begin_on else "off"
        self.__blink_stop_end.custom_value = "off" if end_off else "on"

        self.transit_to(self.__blink_begin)

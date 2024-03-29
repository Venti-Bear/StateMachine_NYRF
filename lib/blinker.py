from lib.finite_state_machine import FiniteStateMachine
from lib.layout import Layout
from lib.state import MonitoredState
from lib.transition import ConditionalTransition
from lib.condition import StateValueCondition, StateEntryDurationCondition

from typing import Callable, Optional, Union
from enum import Enum, auto


class Side(Enum):
    """
    Defines an enumeration of operational states that a system or process can be in.

    OperationalState is an enumeration class that defines four states: UNINITIALIZED,
    IDLE, RUNNING, and TERMINAL_REACHED. Each state is represented by a unique value
    that can be compared to other instances of the same class using equality operators.

    The values for each state are generated automatically using the `auto()` function
    from the `enum` module. This ensures that each state has a unique value that is
    not dependent on its position in the enumeration definition.

    Example usage:
        # Create an OperationalState instance
        state = OperationalState.IDLE

        # Compare two instances of the same class
        if state == OperationalState.RUNNING:
            print("The system is currently running.")

        # Loop through all states in the enumeration
        for state in OperationalState:
            print(state)
    """
    LEFT = auto()
    RIGHT = auto()
    BOTH = auto()
    LEFT_RECIPROCAL = auto()
    RIGHT_RECIPROCAL = auto()

    def __str__(self):
        return self.name


class Blinker(FiniteStateMachine):
    """
    A finite state machine that models a blinking light. The Blinker can be in one of two states - on or off.
    It can also transition between on and off states repeatedly, creating a blinking effect. The Blinker
    can be controlled to turn on, turn off, or blink with customizable settings.
    """
    # __blink_on_cond: StateEntryDurationCondition
    # __blink_stop_on_cond: StateEntryDurationCondition
    # __blink_off_cond: StateEntryDurationCondition
    # __on_duration_cond: StateEntryDurationCondition
    # __off_duration_cond: StateEntryDurationCondition
    # __blink_stop_end: MonitoredState
    # __blink_stop_begin: MonitoredState
    # __blink_begin: MonitoredState
    # __on_duration: MonitoredState
    # __off_duration: MonitoredState
    # __on: MonitoredState
    # __off: MonitoredState

    def __init__(self, off_state_generator: Callable[[], MonitoredState],
                 on_state_generator: Callable[[], MonitoredState]) -> None:
        """
        Initializes a new Blinker object with the given off and on state generators.

        Args:
            off_state_generator: A callable that generates a new MonitoredState object representing the off state.
            on_state_generator: A callable that generates a new MonitoredState object representing the on state.

        Raises:
            TypeError: If off_state_generator or on_state_generator is not callable.
        """
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
        self.__off_duration_cond = StateEntryDurationCondition(
            0.0, self.__off_duration)
        self.__on_duration_cond = StateEntryDurationCondition(
            0.0, self.__on_duration)

        self.__off_duration.add_transition(
            ConditionalTransition(self.__on, self.__off_duration_cond))
        self.__on_duration.add_transition(
            ConditionalTransition(self.__off, self.__on_duration_cond))

        # blink off/on
        self.__blink_off_cond = StateEntryDurationCondition(0.0, blink_off)
        self.__blink_on_cond = StateEntryDurationCondition(0.0, blink_on)

        blink_off.add_transition(ConditionalTransition(
            blink_on, self.__blink_off_cond))
        blink_on.add_transition(ConditionalTransition(
            blink_off, self.__blink_on_cond))

        cond_off = StateValueCondition("off", self.__blink_begin)
        cond_on = StateValueCondition("on", self.__blink_begin)

        self.__blink_begin.add_transition(
            ConditionalTransition(blink_on, cond_on))
        self.__blink_begin.add_transition(
            ConditionalTransition(blink_off, cond_off))

        # stop

        self.__blink_stop_off_cond = StateEntryDurationCondition(
            0.0, blink_stop_off)
        self.__blink_stop_on_cond = StateEntryDurationCondition(
            0.0, blink_stop_on)

        blink_stop_off.add_transition(ConditionalTransition(
            blink_stop_on, self.__blink_stop_off_cond))
        blink_stop_on.add_transition(ConditionalTransition(
            blink_stop_off, self.__blink_stop_on_cond))

        cond_off = StateValueCondition("off", self.__blink_stop_begin)
        cond_on = StateValueCondition("on", self.__blink_stop_begin)

        self.__blink_stop_begin.add_transition(
            ConditionalTransition(blink_stop_on, cond_on))
        self.__blink_stop_begin.add_transition(
            ConditionalTransition(blink_stop_off, cond_off))

        self.__blink_stop_cond = StateEntryDurationCondition(
            0.0, self.__blink_stop_begin)
        transition = ConditionalTransition(
            self.__blink_stop_end, self.__blink_stop_cond)

        blink_stop_off.add_transition(transition)
        blink_stop_on.add_transition(transition)

        cond_off = StateValueCondition("off", self.__blink_stop_end)
        cond_on = StateValueCondition("on", self.__blink_stop_end)

        self.__blink_stop_end.add_transition(
            ConditionalTransition(self.__on, cond_on))
        self.__blink_stop_end.add_transition(
            ConditionalTransition(self.__off, cond_off))


        # add to layout

        layout.add_states(
            {self.__off, self.__on, self.__off_duration, self.__on_duration, blink_off, blink_on, blink_stop_off,
             blink_stop_on, self.__blink_begin, self.__blink_stop_begin, self.__blink_stop_end})

        layout.initial_state = self.__off

        super().__init__(layout, uninitialized=False)

        self.__on_states = {self.__on,
                            self.__on_duration, blink_on, blink_stop_on}
        self.__off_states = {self.__off,
                             self.__off_duration, blink_off, blink_stop_off}

    @property
    def is_on(self):
        return self.current_applicative_state in self.__on_states

    @property
    def is_off(self):
        return self.current_applicative_state in self.__off_states

    def turn_on(self, duration: Optional[Union[float, int]] = None) -> None:
        """
        Turns on the Blinker, with an optional duration argument.

        Args:
            duration: A float or int representing the duration of the on state, in seconds. If None, the Blinker transitions to the on state indefinitely.

        Raises:
            TypeError: If duration is not None, float, or int.
        """
        if not isinstance(duration, (float, int)) and duration is not None:
            raise TypeError("duration must be a float, a int or None")

        if duration is None:
            self.transit_to(self.__on)
        else:
            self.__on_duration_cond.duration = duration
            self.transit_to(self.__on_duration)

    def turn_off(self, duration: Optional[Union[float, int]] = None) -> None:
        """
        Turns off the Blinker, with an optional duration argument.

        Args:
            duration: A float or int representing the duration of the off state, in seconds. If None, the Blinker transitions to the off state indefinitely.

        Raises:
            TypeError: If duration is not None, float, or int.
        """
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
        """
        Blinks the Blinker with customizable settings.

        Args:
            total_duration: A float or int representing the total duration of the blink cycle, in seconds.
            cycle_duration: A float or int representing the duration of one blink cycle, in seconds.
            n_cycles: An int representing the number of blink cycles.
            percent_on: A float or int representing the percentage of time the Blinker is on during a blink cycle. Must be between 0 and 1.
            begin_on: A bool representing whether the blink cycle starts with the Blinker on or off.
            end_off: A bool representing whether the blink cycle ends with the Blinker on or off.

        Raises:
            TypeError: If total_duration, cycle_duration, percent_on, begin_on, or end_off is not None, float, int, or bool.
            ValueError: If percent_on is not between 0 and 1.
            TypeError: If invalid arguments are passed, based on the calling convention.
        """

        if not isinstance(total_duration, (float, int)) and total_duration is not None:
            raise TypeError("total_duration must be a float, a int or None")
        elif not isinstance(cycle_duration, (float, int)) and cycle_duration is not None:
            raise TypeError("cycle_duration must be a float, a int or None")
        elif not isinstance(n_cycles, int) and n_cycles is not None:
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
            self.__blink_stop(total_duration, cycle_duration,
                              percent_on, begin_on, end_off)
        elif total_duration is not None and cycle_duration is None and n_cycles is not None:
            cycle_duration = total_duration / n_cycles
            self.__blink_stop(total_duration, cycle_duration,
                              percent_on, begin_on, end_off)
        elif total_duration is None and cycle_duration is not None and n_cycles is not None:
            total_duration = cycle_duration * n_cycles
            self.__blink_stop(total_duration, cycle_duration,
                              percent_on, begin_on, end_off)
        else:
            raise TypeError("invalid calling convention")

    def __blink(self, cycle_duration: Union[float, int], percent_on: Union[float, int], begin_on: bool) -> None:
        """
        Blinks the Blinker once with the given cycle duration and percentage of time on.

        Args:
            cycle_duration: A float or int representing the duration of one blink cycle, in seconds.
            percent_on: A float or int representing the percentage of time the Blinker is on during a blink cycle. Must be between 0 and 1.
            begin_on: A bool representing whether the blink cycle starts with the Blinker on or off.

        Raises:
            TypeError: If cycle_duration or percent_on is not a float or int.
        """
        on_time = cycle_duration * percent_on
        off_time = cycle_duration - on_time

        self.__blink_begin.custom_value = "on" if begin_on else "off"
        self.__blink_on_cond.duration = on_time
        self.__blink_off_cond.duration = off_time

        self.transit_to(self.__blink_begin)

    def __blink_stop(self, total_duration: Union[float, int], cycle_duration: Union[float, int],
                     percent_on: Union[float, int], begin_on: bool, end_off: bool) -> None:
        """
        Blinks the Blinker repeatedly with the given settings until a total duration is reached.

        Args:
            total_duration: A float or int representing the total duration of the blink cycle, in seconds.
            cycle_duration: A float or int representing the duration of one blink cycle, in seconds.
            percent_on: A float or int representing the percentage of time the Blinker is on during a blink cycle. Must be between 0 and 1.
            begin_on: A bool representing whether the blink cycle starts with the Blinker on or off.
            end
        """
        on_time = cycle_duration * percent_on
        off_time = cycle_duration - on_time

        self.__blink_stop_cond.duration = total_duration

        self.__blink_stop_on_cond.duration = on_time
        self.__blink_stop_off_cond.duration = off_time

        self.__blink_stop_begin.custom_value = "on" if begin_on else "off"
        self.__blink_stop_end.custom_value = "off" if end_off else "on"

        self.transit_to(self.__blink_stop_begin)


class SideBlinkers:
    """
    A class that represents the side blinkers of a given object, controlling the state of the left and right blinkers.

    Attributes:
        __left_blinker (Blinker): The left blinker.
        __right_blinker (Blinker): The right blinker.
    """
    # __left_blinker: Blinker
    # __right_blinker: Blinker

    def __init__(self,
                 left_off_state_generator: Callable[[], MonitoredState],
                 left_on_state_generator: Callable[[], MonitoredState],
                 right_off_state_generator: Callable[[], MonitoredState],
                 right_on_state_generator: Callable[[], MonitoredState]) -> None:
        """
        Initializes the SideBlinkers with the provided state generator callables for left and right blinkers.

        Args:
            left_off_state_generator (Callable[[], MonitoredState]): A callable to generate the off state for the left blinker.
            left_on_state_generator (Callable[[], MonitoredState]): A callable to generate the on state for the left blinker.
            right_off_state_generator (Callable[[], MonitoredState]): A callable to generate the off state for the right blinker.
            right_on_state_generator (Callable[[], MonitoredState]): A callable to generate the on state for the right blinker.
        """

        self.__left_blinker = Blinker(
            left_off_state_generator, left_on_state_generator)
        self.__right_blinker = Blinker(
            right_off_state_generator, right_on_state_generator)

    def is_on(self, side: Side) -> bool:
        """
        Checks if the specified side blinker(s) is/are on.

        Args:
            side (Side): The side to check (LEFT, RIGHT, BOTH, LEFT_RECIPROCAL, or RIGHT_RECIPROCAL).

        Returns:
            bool: True if the specified side blinker(s) is/are on, False otherwise.
        """
        if not isinstance(side, Side):
            raise TypeError("side must be of type Side")
        if side == Side.BOTH:
            return self.__right_blinker.is_on and self.__left_blinker.is_on
        elif side == Side.LEFT:
            return self.__left_blinker.is_on
        elif side == Side.RIGHT:
            return self.__right_blinker.is_on
        elif side == Side.LEFT_RECIPROCAL:
            return self.__left_blinker.is_on and self.__right_blinker.is_off
        elif side == Side.RIGHT_RECIPROCAL:
            return self.__right_blinker.is_on and self.__left_blinker.is_off

    def is_off(self, side: Side) -> bool:
        """
        Checks if the specified side blinker(s) is/are off.

        Args:
            side (Side): The side to check (LEFT, RIGHT, BOTH, LEFT_RECIPROCAL, or RIGHT_RECIPROCAL).

        Returns:
            bool: True if the specified side blinker(s) is/are off, False otherwise.
        """
        if not isinstance(side, Side):
            raise TypeError("side must be of type Side")
        if side == Side.BOTH:
            return self.__right_blinker.is_off and self.__left_blinker.is_off
        elif side == Side.RIGHT:
            return self.__right_blinker.is_off
        elif side == Side.LEFT:
            return self.__left_blinker.is_off
        elif side == Side.LEFT_RECIPROCAL:
            return self.__left_blinker.is_off and self.__right_blinker.is_on
        elif side == Side.RIGHT_RECIPROCAL:
            return self.__right_blinker.is_off and self.__left_blinker.is_on

    def turn_on(self, side: Side, duration: Optional[Union[float, int]] = None) -> None:
        """
        Turns on the specified side blinker(s) for a given duration or indefinitely if duration is not provided.

        Args:
            side (Side): The side to turn on (LEFT, RIGHT, BOTH, LEFT_RECIPROCAL, or RIGHT_RECIPROCAL).
            duration (Optional[Union[float, int]]): The duration for which the blinker(s) should be on, in seconds. None for indefinite.
        """
        if not isinstance(side, Side):
            raise TypeError("side must be of type Side")
        try:
            turn_on_dict = {
                Side.LEFT: lambda: self.__left_blinker.turn_on(duration),
                Side.RIGHT: lambda: self.__right_blinker.turn_on(duration),
                Side.BOTH: lambda: (self.__left_blinker.turn_on(duration), self.__right_blinker.turn_on(duration)),
                Side.LEFT_RECIPROCAL: lambda: (
                    self.__left_blinker.turn_on(duration), self.__right_blinker.turn_off(duration)),
                Side.RIGHT_RECIPROCAL: lambda: (self.__left_blinker.turn_off(
                    duration), self.__right_blinker.turn_on(duration))
            }
            turn_on_func = turn_on_dict.get(side)

            if turn_on_func is None:
                raise ValueError("Invalid Side enum value")

            turn_on_func()

        except (TypeError, IOError) as e:
            raise ValueError("Failed to turn on blinkers")

    def turn_off(self, side: Side, duration: Optional[Union[float, int]] = None) -> None:
        """
        Turns off the specified side blinker(s) for a given duration or indefinitely if duration is not provided.

        Args:
            side (Side): The side to turn off (LEFT, RIGHT, BOTH, LEFT_RECIPROCAL, or RIGHT_RECIPROCAL).
            duration (Optional[Union[float, int]]): The duration for which the blinker(s) should be off, in seconds. None for indefinite.
        """
        if not isinstance(side, Side):
            raise TypeError("side must be of type Side")
        try:
            turn_off_dict = {
                Side.LEFT: lambda: self.__left_blinker.turn_off(duration),
                Side.RIGHT: lambda: self.__right_blinker.turn_off(duration),
                Side.BOTH: lambda: (self.__left_blinker.turn_off(duration), self.__right_blinker.turn_off(duration)),
                Side.LEFT_RECIPROCAL: lambda: (
                    self.__left_blinker.turn_off(duration), self.__right_blinker.turn_on(duration)),
                Side.RIGHT_RECIPROCAL: lambda: (self.__left_blinker.turn_on(
                    duration), self.__right_blinker.turn_off(duration))
            }
            turn_off_func = turn_off_dict.get(side)

            if turn_off_func is None:
                raise ValueError("Invalid Side enum value")

            turn_off_func()

        except (TypeError, IOError) as e:
            raise ValueError("Failed to turn off blinkers")

    def blink(self, side: Side, *, total_duration: Optional[Union[float, int]] = None,
              cycle_duration: Optional[Union[float, int]] = None, n_cycles: Optional[int] = None,
              percent_on: Union[float, int] = 0.5, begin_on: bool = True, end_off: bool = True) -> None:
        """
        Blinks the specified side blinker(s) based on the given parameters.

        Args:
            side (Side): The side to blink (LEFT, RIGHT, BOTH, LEFT_RECIPROCAL, or RIGHT_RECIPROCAL).
            total_duration (Optional[Union[float, int]]): The total duration of the blinking sequence, in seconds. None for indefinite.
            cycle_duration (Optional[Union[float, int]]): The duration of each on-off cycle, in seconds. None for automatic calculation.
            n_cycles (Optional[int]): The number of on-off cycles to perform. None for automatic calculation.
            percent_on (Union[float, int]): The percentage of time each cycle should be on, expressed as a float between 0 and 1 or an integer between 0 and 100.
            begin_on (bool): Whether the blinking sequence should begin with the blinker(s) on (True) or off (False).
            end_off (bool): Whether the blinking sequence should end with the blinker(s) off (True) or maintain their final state (False).
        """
        if not isinstance(side, Side):
            raise TypeError("side must be of type Side")
        try:
            param_dict = {
                'total_duration': total_duration,
                'cycle_duration': cycle_duration,
                'n_cycles': n_cycles,
                'percent_on': percent_on,
                'begin_on': begin_on,
                'end_off': end_off
            }

            param_dict_reciprocal = {
                'total_duration': total_duration,
                'cycle_duration': cycle_duration,
                'n_cycles': n_cycles,
                'percent_on': percent_on,
                'begin_on': not begin_on,
                'end_off': not end_off
            }

            blink_dict = {
                Side.LEFT: lambda: self.__left_blinker.blink(**param_dict),
                Side.RIGHT: lambda: self.__right_blinker.blink(**param_dict),
                Side.BOTH: lambda: (self.__right_blinker.blink(**param_dict),
                                    self.__left_blinker.blink(**param_dict)),
                Side.LEFT_RECIPROCAL: lambda: (self.__left_blinker.blink(**param_dict),
                                               self.__right_blinker.blink(**param_dict_reciprocal)),
                Side.RIGHT_RECIPROCAL: lambda: (self.__right_blinker.blink(**param_dict),
                                                self.__left_blinker.blink(**param_dict_reciprocal))
            }

            blink_func = blink_dict.get(side)

            if blink_func is None:
                raise ValueError("Invalid Side enum value")

            blink_func()

        except (IOError) as e:
            raise ValueError("Failed to blink the blinkers")

    def track(self):
        self.__left_blinker.track()
        self.__right_blinker.track()

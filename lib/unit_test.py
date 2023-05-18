import unittest
from condition import *


class TestConditions(unittest.TestCase):
    def test_always_true_condition(self):
        always_true = AlwaysTrueCondition()
        self.assertTrue(always_true)

    def test_value_condition_true(self):
        initial_value = 10
        expected_value = 10
        value_cond = ValueCondition(initial_value, expected_value)
        self.assertTrue(value_cond)

    def test_value_condition_false(self):
        initial_value = 10
        expected_value = 20
        value_cond = ValueCondition(initial_value, expected_value)
        self.assertFalse(value_cond)

    def test_timed_condition(self):
        duration = 0.1
        timed_cond = TimedCondition(duration=duration, time_reference=time.perf_counter())
        self.assertTrue(timed_cond)
        time.sleep(duration + 0.1)
        self.assertFalse(timed_cond)

    def test_state_entry_duration_condition(self):
        monitored_state = MonitoredState()
        monitored_state._exec_entering_action()
        duration = 0.1
        entry_duration_cond = StateEntryDurationCondition(duration, monitored_state)
        self.assertFalse(entry_duration_cond)
        # monitored_state.update_entry_time()
        time.sleep(duration + 0.1)
        self.assertTrue(entry_duration_cond)

    def test_state_entry_count_condition(self):
        monitored_state = MonitoredState()
        entry_count_cond = StateEntryCountCondition(1, monitored_state)
        self.assertFalse(entry_count_cond)
        monitored_state._exec_entering_action()
        # monitored_state.update_entry_count()
        self.assertTrue(entry_count_cond)

    def test_state_value_condition_true(self):
        monitored_state = MonitoredState()
        monitored_state.custom_value = "value"
        value_cond = StateValueCondition("value", monitored_state)
        self.assertTrue(value_cond)

    def test_state_value_condition_false(self):
        monitored_state = MonitoredState()
        monitored_state.custom_value = "value"
        value_cond = StateValueCondition("not the value", monitored_state)
        self.assertFalse(value_cond)

    def test_all_conditions_true(self):
        always_true = AlwaysTrueCondition()

        # Create a AllConditions object and add the conditions
        all_conditions = AnyConditions()
        all_conditions.add_condition(always_true)
        all_conditions.add_condition(always_true)

        self.assertTrue(all_conditions)

    def test_all_conditions_false(self):
        always_true = AlwaysTrueCondition()
        always_false = AlwaysTrueCondition(inverse=True)

        # Create a AllConditions object and add the conditions
        all_conditions = AllConditions()
        all_conditions.add_condition(always_true)
        all_conditions.add_condition(always_false)

        self.assertFalse(all_conditions)

    def test_any_conditions_true(self):
        always_false = AlwaysTrueCondition(inverse=True)
        always_true = AlwaysTrueCondition()

        # Create a AnyConditions object and add the conditions
        any_conditions = AnyConditions()
        any_conditions.add_condition(always_true)
        any_conditions.add_condition(always_false)

        self.assertTrue(any_conditions)

    def test_any_conditions_false(self):
        always_false = AlwaysTrueCondition(inverse=True)

        # Create a AnyConditions object and add the conditions
        any_conditions = AnyConditions()
        any_conditions.add_condition(always_false)
        any_conditions.add_condition(always_false)

        self.assertFalse(any_conditions)

    def test_none_conditions_true(self):
        always_false = AlwaysTrueCondition(inverse=True)

        # Create a NoneConditions object and add the conditions
        none_conditions = NoneConditions()
        none_conditions.add_condition(always_false)
        none_conditions.add_condition(always_false)

        self.assertTrue(none_conditions)

    def test_none_conditions_false(self):
        always_false = AlwaysTrueCondition(inverse=True)
        always_true = AlwaysTrueCondition()

        # Create a NoneConditions object and add the conditions
        none_conditions = NoneConditions()
        none_conditions.add_condition(always_false)
        none_conditions.add_condition(always_true)

        self.assertFalse(none_conditions)


if __name__ == '__main__':
    unittest.main()

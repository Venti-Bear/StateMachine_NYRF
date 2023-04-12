import unittest
from state import MonitoredState
from condition import *

class TestConditions(unittest.TestCase):
    def test_always_true_condition(self):
        always_true = AlwaysTrueCondition()
        self.assertTrue(always_true.compare())
        always_true_inverse = AlwaysTrueCondition(inverse=True)
        self.assertFalse(always_true_inverse.compare())

    def test_value_condition(self):
        initial_value = 10
        expected_value = 20
        value_cond = ValueCondition(initial_value, expected_value)
        self.assertFalse(value_cond.compare())
        value_cond_inverse = ValueCondition(initial_value, expected_value, inverse=True)
        self.assertTrue(value_cond_inverse.compare())

    def test_timed_condition(self):
        duration = 0.1
        timed_cond = TimedCondition(duration=duration)
        time.sleep(duration + 0.1)
        self.assertTrue(timed_cond.compare())
        timed_cond_inverse = TimedCondition(duration=duration, inverse=True)
        self.assertFalse(timed_cond_inverse.compare())

    def test_state_entry_duration_condition(self):
        monitored_state = MonitoredState()
        monitored_state.custom_value = "value"
        duration = 0.1
        entry_duration_cond = StateEntryDurationCondition(duration, monitored_state)
        self.assertFalse(entry_duration_cond.compare())
        monitored_state.update_entry_time()
        time.sleep(duration + 0.1)
        self.assertTrue(entry_duration_cond.compare())
        entry_duration_cond_inverse = StateEntryDurationCondition(duration, monitored_state, inverse=True)
        self.assertTrue(entry_duration_cond_inverse.compare())

    def test_state_entry_count_condition(self):
        monitored_state = MonitoredState()
        monitored_state.custom_value = "value"
        entry_count_cond = StateEntryCountCondition(2, monitored_state)
        self.assertFalse(entry_count_cond.compare())
        monitored_state.update_entry_count()
        self.assertFalse(entry_count_cond.compare())
        monitored_state.update_entry_count()
        self.assertTrue(entry_count_cond.compare())
        entry_count_cond_inverse = StateEntryCountCondition(2, monitored_state, inverse=True)
        self.assertFalse(entry_count_cond_inverse.compare())

    def test_state_value_condition(self):
        monitored_state = MonitoredState()
        monitored_state.custom_value = "value"
        value_cond = StateValueCondition("value", monitored_state)
        self.assertTrue(value_cond.compare())
        value_cond_inverse = StateValueCondition("value", monitored_state, inverse=True)
        self.assertFalse(value_cond_inverse.compare())

    def test_all_conditions(self):
        always_true = AlwaysTrueCondition()
        value_cond = ValueCondition(10, 20)
        timed_cond = TimedCondition(duration=0.1)
        monitored_state = MonitoredState()
        monitored_state.custom_value = "value"
        entry_duration_cond = StateEntryDurationCondition(0.1, monitored_state)
        entry_count_cond = StateEntryCountCondition(2, monitored_state)
        value_cond = StateValueCondition("value", monitored_state)
        all_conds = AllConditions()
        all_conds.add_conditions([always_true, value_cond, timed_cond, entry_duration_cond, entry_count_cond])
        self.assertFalse(all_conds.compare())
        monitored_state.update_entry_count()
        monitored_state.update_entry_time()
        time.sleep(0.2)
        self.assertTrue(all_conds.compare())

    def test_any_conditions(self):
        always_true = AlwaysTrueCondition()
        value_cond = ValueCondition(10, 20)
        timed_cond = TimedCondition(duration=0.1)
        monitored_state = MonitoredState()
        monitored_state.custom_value = "value"
        entry_duration_cond = StateEntryDurationCondition(0.1, monitored_state)
        entry_count_cond = StateEntryCountCondition(2, monitored_state)

        # AlwaysTrueCondition should always pass
        self.assertTrue(always_true.check(None))

        # ValueCondition should pass for values between 10 and 20
        self.assertTrue(value_cond.check(15))
        self.assertFalse(value_cond.check(5))
        self.assertFalse(value_cond.check(25))

        # TimedCondition should pass for the specified duration
        time.sleep(0.2)
        self.assertTrue(timed_cond.check(None))

        # MonitoredState should pass if the monitored value is set
        self.assertTrue(monitored_state.check(None))

        # StateEntryDurationCondition should pass if state has been entered for at least the specified duration
        time.sleep(0.2)
        self.assertTrue(entry_duration_cond.check(None))

        # StateEntryCountCondition should pass if state has been entered the specified number of times
        self.assertTrue(entry_count_cond.check(None))
        monitored_state.add_state_entry()
        self.assertFalse(entry_count_cond.check(None))
        monitored_state.add_state_entry()
        self.assertTrue(entry_count_cond.check(None))

    def test_none_conditions(self):
        always_true = AlwaysTrueCondition()
        value_cond = ValueCondition(10, 20)
        timed_cond = TimedCondition(duration=0.1)
        monitored_state = MonitoredState()
        monitored_state.custom_value = "value"
        entry_duration_cond = StateEntryDurationCondition(0.1, monitored_state)
        entry_count_cond = StateEntryCountCondition(1, monitored_state)

        # Create a NoneConditions object and add the conditions
        none_conditions = NoneConditions()
        none_conditions.add_condition(always_true)
        none_conditions.add_condition(value_cond)
        none_conditions.add_condition(timed_cond)
        none_conditions.add_condition(entry_duration_cond)
        none_conditions.add_condition(entry_count_cond)

        # Verify that the conditions fail
        assert bool(none_conditions) is False

        # Reset the monitored state's entry count
        monitored_state.reset_entry_count()

        # Wait for the timed condition to expire
        time.sleep(0.2)

        # Verify that the conditions pass
        assert bool(none_conditions) is True
  
      
if __name__ == '__main__':
    unittest.main()
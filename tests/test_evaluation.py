import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
import numpy as np
from evaluate_detector import alarm_timing, summarize


class EvaluationTests(unittest.TestCase):
    def test_latency_includes_the_observation_interval(self):
        result=alarm_timing(np.array([False,False,True,False]),2,20)
        self.assertEqual(result["delay_seconds"],.05)

    def test_premature_alarm_is_not_credited_as_post_injection_detection(self):
        result=alarm_timing(np.array([True,False,False,False]),2,20)
        self.assertTrue(result["premature_alarm"])
        self.assertIsNone(result["first_post_injection_alarm_action"])
        self.assertIsNone(result["delay_seconds"])

    def test_recovered_perturbation_is_not_labeled_task_failure(self):
        row={"condition":"arm_hold","final_success":True,"alarm":True,"length":5,
             "alarm_steps_count":1,"first_post_injection_alarm_action":2,
             "delay_seconds":.05,"premature_alarm":False}
        result=summarize([row])
        self.assertEqual(result["true_positive"],0)
        self.assertEqual(result["false_positive"],1)
        self.assertEqual(result["recovered_trial_alarms"],1)
        self.assertIsNone(result["task_failure_recall"])


if __name__=="__main__":
    unittest.main()

import sys
sys.path.append("/Users/hoischen/CTA/TransientsHandler")

from utilities.observatories import CTA_North

from processing import observation_windows
from datetime import datetime
import astropy.units as u

from processing import cuts


import unittest


class obs_window_test_case:
    def init(self):
        self.case_name = None
        self.ra = None
        self.dec = None
        self.time = None
        self.site = None

        self.zenith_min = None
        self.max_delay = None
        self.min_duration = None
        self.allowed_brightness = None

        self.expected_delay = None
        self.expected_start = None
        self.expected_end = None
        self.expected_duration = None

    def setup_prompt_case(self):
        self.case_name = "GRB190114C-prompt"
        self.ra = 54.510
        self.dec = -26.939
        self.time = datetime(2019, 1, 11, 20, 57, 23)
        self.site = CTA_North()

        self.zenith_min = 70 * u.deg
        self.max_delay = 10 * u.h
        self.min_duration = 10 * u.min
        self.allowed_brightness = None

        '''
        OBSERVATION WINDOW:
        * Ra, Dec                    : 54.51, -26.94
        * delay                      : 0.01 h
        * start time                 : 2019-01-11 20:58:01.132075
        * end time                   : 2019-01-11 22:00:33.962264
        * duration                   : 1.04 h
        '''

        self.expected_delay = 0.011 * u.h
        self.expected_start = datetime(2019, 1, 11, 20, 58, 1)
        self.expected_end = datetime(2019, 1, 11, 22, 0, 33)
        self.expected_duration = 1.042 * u.h

        return self

    def setup_prompt_case_2(self):
        self.case_name = "GRB190114C-prompt 22222"
        self.ra = 54.510
        self.dec = -26.939
        self.time = datetime(2019, 1, 14, 20, 57, 3)
        self.site = CTA_North()

        self.zenith_min = 70 * u.deg
        self.max_delay = 2 * u.h
        self.min_duration = 10 * u.min
        self.allowed_brightness = None

        self.expected_delay = 0 * u.h
        self.expected_start = datetime(2019, 10, 4, 21, 33, 57)
        self.expected_end = datetime(2019, 10, 5, 2, 41, 53)
        self.expected_duration = 5.13 * u.h

        return self


class TestObservationWindowCalculation(unittest.TestCase):
    def prepare_testcases(self):
        self.test_cases = [obs_window_test_case().setup_prompt_case()]
                           # obs_window_test_case().setup_prompt_case_2()]

    def test_window_calculations(self):
        self.prepare_testcases()

        window = observation_windows.ObservationWindow()

        for case in self.test_cases:
            print("... testing observation conditions of", case.case_name)
            self.assertTrue(window.test(case.ra, case.dec, case.time, case.site, case.zenith_min,
                            case.max_delay, case.min_duration, case.allowed_brightness,
                            case.expected_delay, case.expected_start, case.expected_end,
                            case.expected_duration))


class TestCutEvaluation(unittest.TestCase):
    def prepare_cut_tests(self):
        test_definitions = {cut_conditions(True, "==", True): True,
                            cut_conditions("True", "==", True): True,
                            cut_conditions(True, "==", False): False,
                            cut_conditions("abc", "==", "abc"): True,
                            cut_conditions('foo', "==", "bar"): False,
                            cut_conditions(10, "==", 10): True,
                            cut_conditions("10", "==", 10): True,
                            cut_conditions(10 * u.h, "==", 10 * 60 * u.min): True,
                            cut_conditions(10 * u.h, "==", 1 * u.s): False,
                            cut_conditions(10 * u.h, "==", "10 h"): True,
                            cut_conditions(10 * u.h, "==", "5 K"): False,
                            cut_conditions(12.5 * u.deg, "==", "12.5 deg"): True,
                            cut_conditions(1.09, ">", 1.2): True,
                            cut_conditions(125.2, ">", 5.5): False}

        return test_definitions

    def test_cut_evaluation(self):
        cuts_to_test = self.prepare_cut_tests()

        for cut_conds, expected_result in cuts_to_test.items():
            name = cut_conds.name
            print(name, "...")
            cut = cuts.cut(name, cut_conds.required, cuts.Comparator(cut_conds.comp),
                           cuts.CutTypes.common_cuts, False, cut_conds.actual)
            cut.evaluate()
            result = (cut.performed and cut.passed)
            comp = (result == expected_result)
            if not comp:
                print("cut: %s failed..." % (name))
            self.assertTrue(comp)


class cut_conditions:
    def __init__(self, required, comp, actual):
        self.required = required
        self.comp = comp
        self.actual = actual
        self.name = "%s %s %s" % (required, comp, actual)


class TestAlertEntry(unittest.TestCase):
    def prepare_alert_entry_test(self):
        pass

    def test_alert_entry(self):
        pass


if __name__ == "__main__":
    unittest.main()

# This script analysses swift alerts as they come in.

import sys
import os
sys.path.append("/Users/hoischen/CTA/github/TransientsHandler")

from broker_system import entry_points as th
from utilities.testing_conditions import TestingConditions as tc
from datetime import datetime


def main():

    TH_main_path = "/Users/hoischen/CTA/github/TransientsHandler"
    os.environ['TH_site_config'] = TH_main_path + "/th_site_config.json"

    # TODO: argument parser
    # definitions_path = "followup_criteria_definition_swift_bat_example.json"
    # received_alert_path = "ivo___nasa_gsfc_gcn_SWIFT_BAT_GRB_Pos_927839-841"
    received_alert_path = "ivo___nasa_gsfc_gcn_SWIFT_BAT_GRB_Pos_883832-433"

    alert_path = TH_main_path + '/tests/test_voevent_alerts/' + received_alert_path

    # test_conditions = tc(datetime(2019, 10, 4, 21, 33, 55))
    test_conditions = tc(datetime(2019, 1, 11, 20, 57, 23))

    th.alert_entry(alert_path, th.alert_origin.injected_voevent, test_conditions)
    # th.alert_entry(alert_path, th.alert_origin.injected_voevent)


if __name__ == "__main__":
    main()

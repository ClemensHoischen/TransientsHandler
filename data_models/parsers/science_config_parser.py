# common parsing functionality of the followup criteria definitions
# needed by scientific alert analysis scripts and other parts of the
# TH. This is a temporary solution and shall be superseeded once
# a stable format and implementation of the follow-up criteria are found.

from astropy import units as u
from astropy.units import Quantity

import data_models.science_config as sci_cfg


def parse_allowed_alert_types(data):
    parsed_allowed_alert_types = []
    for d in data:
        allowed_type = sci_cfg.allowed_alert_types()
        allowed_type.experiment = data[d][0]
        allowed_type.alert_type = data[d][1]
        parsed_allowed_alert_types.append(allowed_type)

    return parsed_allowed_alert_types


def parse_proposal_details(data):
    details = sci_cfg.proposal_details()
    details.proposal_id = data['ProposalID']
    details.proposal_pi = data['ProposalPI']
    details.proposal_type = data["ProposalType"]
    details.proposal_title = data['ProposalTitle']
    return details


def parse_observation_config(data):
    obs_config = sci_cfg.observation_config()
    obs_config.priority = data['Priority']
    obs_config.intended_action = data['IntendedAction']
    obs_config.urgency = data['Urgency']
    obs_config.use_custom_coords = data['UseCustomCoords']
    obs_config.exposure = Quantity(data['MaxExposure'])
    obs_config.number_blocks = data['NumberObservationBlocks']
    obs_config.pointing_mode.setup(data['PointingMode'])
    obs_config.rta_configs.setup(data['RTA_configs'])
    return obs_config


def parse_observation_window_requiremnts(data):
    window_reqs = sci_cfg.obs_window_requirements()

    zenith = data['MaximumZenithAngle']
    window_reqs.max_zenith_angle = zenith[0] * u.Unit(zenith[1])

    duration = data['MinimumWindowDuration']
    window_reqs.min_window_duration = duration[0] * u.Unit(duration[1])

    delay = data['MaximumDelayToEvent']
    window_reqs.max_delay_to_event = delay[0] * u.Unit(delay[1])

    window_reqs.min_nsb_range = data['SkyQuality']['min_nsb_range']
    window_reqs.max_nsb_range = data['SkyQuality']['max_nsb_range']
    window_reqs.illumination = data['SkyQuality']['illumination']

    return window_reqs


def parse_notification_options(data):
    notify_opts = sci_cfg.notification_options()
    notify_opts.HMI_notify_on_received = data['NotifyHMI_OnReceived']
    notify_opts.HMI_notify_on_accepted = data['NotifyHMI_OnCriteriaFulfilled']
    notify_opts.SAG_notify_on_received = data['NotifySAG_OnReceived']
    notify_opts.SAG_notify_on_accepted = data['NotifySAG_OnCriteriaFulfilled']
    notify_opts.fill()

    return notify_opts


def parse_science_cases(data):
    cases = data.items()
    for case in cases:
        print("-----")
        print(case)
        print("-----")
    proc_cases = [sci_cfg.science_case(case) for case in cases]
    return proc_cases

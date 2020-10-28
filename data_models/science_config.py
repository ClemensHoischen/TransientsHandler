'''
This is the central definition point of scinence configurations.
A science configuration is initated from the path of the file.
The relevant parsing functionalitiy is contained in parsers/science_configparser.py

All sub sections of the science configurations have there own object definition which
is also defined here.
'''

import json

from data_models.parsers import science_config_parser as sci_conf_parser
from alert_processor import cuts
from utilities import observation_types


class ScienceConfiguration:
    ''' main object containing the science configuration info '''
    def __init__(self, cfg_path):
        ''' initiates the fill object from the config file path '''
        self.criteria_definition_path = cfg_path
        print("--->", cfg_path)
        with open(cfg_path, "r") as read_file:
            self.data = json.load(read_file)
        self.parse()
        self.pointing_pattern = None

    def parse(self):
        ''' parsing all sections of the config file one by one .
            this is called by __init__()'''
        self.name = self.data['Name']
        proposal_data = self.data["ProposalDetails"]
        self.proposal_details = sci_conf_parser.parse_proposal_details(proposal_data)
        obs_cfg_data = self.data["ObservationConfig"]
        self.observation_config = sci_conf_parser.parse_observation_config(obs_cfg_data)
        allowed_types_data = self.data['AllowedAlertTypes']
        self.allowed_alert_types = sci_conf_parser.parse_allowed_alert_types(allowed_types_data)
        self.cut_collection = cuts.CutCollection(self.data['ProcessingCuts'])
        obs_window_req_data = self.data['ObservationWindowRequirements']
        self.obsevation_window_reqs = sci_conf_parser.parse_observation_window_requiremnts(obs_window_req_data)
        notify_data = self.data['Notifications']
        self.notification_opts = sci_conf_parser.parse_notification_options(notify_data)
        self.detections_public = self.data['DetectionsPublic']
        self.followup_public = self.data["ActionPublic"]

    def __str__(self):
        header = "configuration for %s" % self.criteria_definition_path
        out = "# # # %s # # #\n" % header
        out += "%s" % self.proposal_details
        out += "%s\n" % self.observation_config

        for alert_type in self.allowed_alert_types:
            out += "%s" % alert_type

        out += "%s" % self.notification_opts

        out += str(self.cut_collection)

        return out

    def get_summary(self):
        ''' produces a consice summary of the configuration for the alert summary '''
        # name  ,  priority , intended action
        out = "{: <20} {: <30}\n".format("Name:", self.name)
        out += "{: <20} {: <10}\n".format("Priority:", self.observation_config.priority)
        out += "{: <20} {: <10}\n".format("Intended Action", self.observation_config.intended_action)
        out += "{: <20} {}\n".format("Acceptd:", self.cut_collection.result())
        return out


class ObservationConfig:
    ''' object for the observation config section of the science configuration '''
    def __init__(self):
        self.priority = None
        self.intended_action = None
        self.urgency = None
        self.use_custom_coords = None
        self.pointing_mode = PointingMode()
        self.sag_configs = SAGConfigs()

    def __str__(self):
        head = "\n Observation Configuration\n"
        out_map = {" * Priority": self.priority,
                   " * Intended Action": self.intended_action,
                   " * Urgency": self.urgency,
                   " * Use Custom Coordinates": self.use_custom_coords,
                   " * Pointing Mode": self.pointing_mode,
                   " * SAG Configurations": self.sag_configs}

        out = head
        for name, val in out_map.items():
            out += "{: <30} : {}\n".format(name, val)

        return out


class AllowedAlertTypes:
    ''' object for the allowed alert types secfion from the science configurations '''
    def __init__(self):
        self.experiment = None
        self.alert_type = None

    def __str__(self):
        name = " * Alert Type"
        val = "%s from %s is allowed\n" % (self.alert_type, self.experiment)
        return "{: <30} : {}".format(name, val)


class ProposalDetails:
    ''' object for the proposal details section from the science configurations '''
    def __init__(self):
        self.proposal_id = None
        self.proposal_pi = None
        self.proposal_title = None
        self.proposal_type = None
        self.detections_public = None
        self.followup_public = None
        self.assumed_timescales = None
        self.allowed_arrays = None

    def __str__(self):
        head = " PROPOSAL DETAILS\n"
        out_map = {" * Proposal ID": self.proposal_id,
                   " * Proposal Title": self.proposal_title,
                   " * Proposal Type": self.proposal_type,
                   " * Proposal PI": self.proposal_pi}
        out = head
        for name, val in out_map.items():
            out += "{: <30} : {}\n".format(name, val)

        return out


class ObsWindowRequirements:
    ''' object for the observation window requirements
        from the science configurtation '''
    def __init__(self):
        self.max_zenith_angle = None
        self.min_window_duration = None
        self.max_delay_to_event = None

        #sky quality parameters (see ObservingConditions ICD, needed for SBs)
        self.min_nsb = None
        self.max_nsb = None
        self.illumination = None

    def __str__(self):
        out_map = {"   * Max. Zenith angle": self.max_zenith_angle,
                   "   * Min. Window duration": self.min_window_duration,
                   "   * Max. Delay to Event": self.max_delay_to_event,
                   "   * Min. allowed NSB": self.min_nsb,
                   "   * Max. allowed NSB": self.max_nsb,
                   "   * Illumination": self.illumination}
        out = ""
        for name, val in out_map.items():
            out += "{: <30} : {}\n".format(name, val)
        return out


class NotificationOptions:
    ''' object for the notification options from the science configurations '''
    def __init__(self):
        self.sag_notify_on_received = None
        self.sag_notify_on_accepted = None
        self.hmi_notify_on_received = None
        self.hmi_notify_on_accepted = None
        self.sts_notify_on_received = None
        self.sts_notify_on_accepted = None

    def fill(self):
        ''' main functions to fill this object '''
        self.notify_map = {"hmi_notify_on_received": self.hmi_notify_on_received,
                           "hmi_notify_on_accepted": self.hmi_notify_on_accepted,
                           "sag_notify_on_received": self.sag_notify_on_received,
                           "sag_notify_on_accepted": self.sag_notify_on_accepted,
                           "sts_notify_on_received": self.sts_notify_on_received,
                           "sts_notify_on_accepted": self.sts_notify_on_accepted}

        self.on_received_map = {"hmi_notify_on_received": self.hmi_notify_on_received,
                                "sag_notify_on_received": self.sag_notify_on_received,
                                "sts_notify_on_received": self.sts_notify_on_received}

        self.on_accepted_map = {"hmi_notify_on_accepted": self.hmi_notify_on_accepted,
                                "sag_notify_on_accepted": self.sag_notify_on_accepted,
                                "sts_notify_on_accepted": self.sag_notify_on_accepted}

        self.notify_received_to = []
        if self.hmi_notify_on_received:
            self.notify_received_to.append("HMI")
        if self.sag_notify_on_received:
            self.notify_received_to.append("SAG")
        if self.sts_notify_on_received:
            self.notify_received_to.append("STS")

        self.notify_accepted_to = []
        if self.hmi_notify_on_accepted:
            self.notify_accepted_to.append("HMI")
        if self.sag_notify_on_accepted:
            self.notify_accepted_to.append("SAG")
        if self.sts_notify_on_accepted:
            self.notify_accepted_to.append("STS")

    def __str__(self):
        sag_notices = "OnReceived: %s, OnAccepted: %s\n" % (self.sag_notify_on_received,
                                                            self.sag_notify_on_accepted)
        hmi_notices = "OnReceived: %s, OnAccepted: %s\n" % (self.hmi_notify_on_received,
                                                            self.hmi_notify_on_accepted)
        out = " * Notification Options:\n"
        out += "{: <30} : {}".format("   * Notifications to SAG", sag_notices)
        out += "{: <30} : {}".format("   * Notifications to HMI", hmi_notices)
        out += " notify on received:\n"
        for rec_to in self.notify_received_to:
            out += " - %s " % rec_to

        return out

    def any_on_received(self):
        ''' retrieves all systems that should be notified
        whenever a cetain follow-up opprotunity is received'''
        on_received = any([self.sag_notify_on_received,
                           self.hmi_notify_on_received,
                           self.sts_notify_on_received])
        return on_received

    def any_on_accepted(self):
        ''' retrieves all systems that should be notified
        whenever a certain follow-up opportuntiy fulfills all
        criteria '''
        on_acceptd = any([self.sag_notify_on_accepted,
                          self.hmi_notify_on_accepted,
                          self.sts_notify_on_accepted])
        return on_acceptd


class PointingMode:
    ''' object for the pointing mode section of the science configurtaion '''
    def __init__(self):
        self.obs_type = None

    def __str__(self):
        return str(self.obs_type)

    def setup(self, data):
        ''' main setup function selecting the specific pointing type '''
        if data['Type'] == "Wobble":
            return self.setup_wobble(data)
        else:
            return None

    def setup_wobble(self, data):
        ''' setup function for wobble type '''
        obs_mode = observation_types.Wobble(data['offset'],
                                            data['angle'])
        return obs_mode


class SAGConfigs:
    ''' object containg the SAG configurations from the science configuration '''
    def __init__(self):
        self.default = True
        self.short_transient = False

    def __str__(self):
        return "Default: %s, Short Transients: %s" % (self.default, self.short_transient)

    def setup(self, data):
        ''' main setup function '''
        self.short_transient = data['ShortTransient']
        self.default = data['Default']

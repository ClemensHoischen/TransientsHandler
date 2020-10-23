import json

import parsers.science_config_parser as sci_conf_parser
from processing import cuts
from utilities import observation_types


class science_configuration:
    def __init__(self, cfg_path):
        self.criteria_definition_path = cfg_path
        print("--->", cfg_path)
        with open(cfg_path, "r") as read_file:
            self.data = json.load(read_file)
        self.parse()
        self.pointing_pattern = None

    def parse(self):
        self.name = self.data['Name']
        self.proposal_details = sci_conf_parser.parse_proposal_details(self.data["ProposalDetails"])
        self.observation_config = sci_conf_parser.parse_observation_config(self.data["ObservationConfig"])
        self.allowed_alert_types = sci_conf_parser.parse_allowed_alert_types(self.data['AllowedAlertTypes'])
        self.cut_collection = cuts.CutCollection(self.data['ProcessingCuts'])
        self.obsevation_window_reqs = sci_conf_parser.parse_observation_window_requiremnts(self.data['ObservationWindowRequirements'])
        self.notification_opts = sci_conf_parser.parse_notification_options(self.data['Notifications'])
        self.detections_public = self.data['DetectionsPublic']
        self.followup_public = self.data["ActionPublic"]

    def __str__(self):
        header = "configuration for %s" % self.criteria_definition_path
        out = "# # # %s # # #\n" % header
        out += "%s" % self.proposal_details
        out += "%s\n" % self.observation_config

        for at in self.allowed_alert_types:
            out += "%s" % at

        out += "%s" % self.notification_opts

        out += str(self.cut_collection)

        return out

    def get_summary(self):
        # name  ,  priority , intended action
        out = "{: <20} {: <30}\n".format("Name:", self.name)
        out += "{: <20} {: <10}\n".format("Priority:", self.observation_config.priority)
        out += "{: <20} {: <10}\n".format("Intended Action", self.observation_config.intended_action)
        out += "{: <20} {}\n".format("Acceptd:", self.cut_collection.result())
        return out


class observation_config:
    def __init__(self):
        self.priority = None
        self.intended_action = None
        self.urgency = None
        self.use_custom_coords = None
        self.pointing_mode = pointing_mode()
        self.rta_configs = rta_configs()

    def __str__(self):
        head = "\n Observation Configuration\n"
        out_map = {" * Priority": self.priority,
                   " * Intended Action": self.intended_action,
                   " * Urgency": self.urgency,
                   " * Use Custom Coordinates": self.use_custom_coords,
                   " * Pointing Mode": self.pointing_mode,
                   " * RTA Configurations": self.rta_configs}

        out = head
        for name, val in out_map.items():
            out += "{: <30} : {}\n".format(name, val)

        return out


class allowed_alert_types:
    def __init__(self):
        self.experiment = None
        self.alert_type = None

    def __str__(self):
        name = " * Alert Type"
        val = "%s from %s is allowed\n" % (self.alert_type, self.experiment)
        return "{: <30} : {}".format(name, val)


class proposal_details:
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


class obs_window_requirements:
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


class notification_options:
    def __init__(self):
        self.SAG_notify_on_received = None
        self.SAG_notify_on_accepted = None
        self.HMI_notify_on_received = None
        self.HMI_notify_on_accepted = None
        self.STS_notify_on_received = None
        self.STS_notify_on_accepted = None

    def fill(self):
        self.notify_map = {"HMI_notify_on_received": self.HMI_notify_on_received,
                           "HMI_notify_on_accepted": self.HMI_notify_on_accepted,
                           "SAG_notify_on_received": self.SAG_notify_on_received,
                           "SAG_notify_on_accepted": self.SAG_notify_on_accepted,
                           "STS_notify_on_received": self.STS_notify_on_received,
                           "STS_notify_on_accepted": self.STS_notify_on_accepted}

        self.on_received_map = {"HMI_notify_on_received": self.HMI_notify_on_received,
                                "SAG_notify_on_received": self.SAG_notify_on_received,
                                "STS_notify_on_received": self.STS_notify_on_received}

        self.on_accepted_map = {"HMI_notify_on_accepted": self.HMI_notify_on_accepted,
                                "SAG_notify_on_accepted": self.SAG_notify_on_accepted,
                                "STS_notify_on_accepted": self.STS_notify_on_accepted}

        self.notify_received_to = []
        if self.HMI_notify_on_received:
            self.notify_received_to.append("HMI")
        if self.SAG_notify_on_received:
            self.notify_received_to.append("SAG")
        if self.STS_notify_on_received:
            self.notify_received_to.append("STS")

        self.notify_accepted_to = []
        if self.HMI_notify_on_accepted:
            self.notify_accepted_to.append("HMI")
        if self.SAG_notify_on_accepted:
            self.notify_accepted_to.append("SAG")
        if self.STS_notify_on_accepted:
            self.notify_accepted_to.append("STS")

    def __str__(self):
        sag_notices = "OnReceived: %s, OnAccepted: %s\n" % (self.SAG_notify_on_received, self.SAG_notify_on_accepted)
        hmi_notices = "OnReceived: %s, OnAccepted: %s\n" % (self.HMI_notify_on_received, self.HMI_notify_on_accepted)
        out = " * Notification Options:\n"
        out += "{: <30} : {}".format("   * Notifications to SAG", sag_notices)
        out += "{: <30} : {}".format("   * Notifications to HMI", hmi_notices)
        out += " notify on received:\n"
        for to in self.notify_received_to:
            out += " - %s " % to

        return out

    def any_on_received(self):
        on_received = any([self.SAG_notify_on_received,
                           self.HMI_notify_on_received,
                           self.STS_notify_on_received])
        return on_received

    def any_on_accepted(self):
        on_acceptd = any([self.SAG_notify_on_accepted,
                          self.HMI_notify_on_accepted,
                          self.STS_notify_on_accepted])
        return on_acceptd


class pointing_mode:
    def __init__(self):
        self.obs_type = None

    def __str__(self):
        return str(self.obs_type)

    def setup(self, data):
        if data['Type'] == "Wobble":
            return self.setup_wobble(data)
        else:
            return None

    def setup_wobble(self, data):
        obs_mode = observation_types.wobble()
        obs_mode.offset = data['offset']
        obs_mode.angle = data['angle']
        return obs_mode


class rta_configs:
    def __init__(self):
        self.default = True
        self.short_transient = False

    def __str__(self):
        return "Default: %s, Short Transients: %s" % (self.default, self.short_transient)

    def setup(self, data):
        self.short_transient = data['ShortTransient']
        self.default = data['Default']

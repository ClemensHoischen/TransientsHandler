''' module of the communicator that produces the output and distributes
it to other ACADA sub-systems according to configuration.

Also generates the alert summaries and stores them.
'''

from communicator import alert_summary


class Communicator:
    ''' maion communicator class '''
    def __init__(self):
        self.all_matches = None
        self.accepted_matches = None
        self.summary = None

    def communicate_results(self):
        self.produce_summaries()
        for match in self.all_matches:
            print(match.summary)

    def register_all_matches(self, matches):
        self.all_matches = matches

    def register_accepted_matches(self, matches):
        self.accepted_matches = matches

    def produce_summaries(self):
        if self.all_matches:
            for match in self.all_matches:
                summary = alert_summary.alert_summary(match)
                match.summary = summary.full_summary

    def communicate_accepted(self, sci_alert_and_cfg):
        self.sci_alert = sci_alert_and_cfg.science_alert
        self.sci_cfg = sci_alert_and_cfg.science_config

        if self.sci_cfg.notification_opts.HMI_notify_on_accepted:
            alert_for_hmi = HMI_alert(self.sci_alert, self.sci_cfg, "follow-up accpeted")
            print(alert_for_hmi.hmi_alert)

    def communicate_received(self, sci_alert_and_cfg):
        print("COMMUNICATE_RECEIVED")
        self.sci_alert = sci_alert_and_cfg.science_alert
        self.sci_cfg = sci_alert_and_cfg.science_config
        notify_received_to = self.sci_cfg.notification_opts.notify_received_to
        print(notify_received_to)

        for to in notify_received_to:
            print("^" * 30)
            print("notifying %s" % to)
            print("received the alert {}, matching to confing {}".format(self.sci_alert.ivorn,
                                                                         self.sci_cfg.name))
            if to is "HMI":
                alert_for_hmi = HMI_alert(self.sci_alert, self.sci_cfg,
                                          "received interesting alert")
                print(alert_for_hmi.hmi_alert)

            print("^" * 30)


class HMI_alert:
    ''' class for alerts aimed at the HMI '''
    def __init__(self, sci_alert, sci_cfg, notice_str):
        self.sci_alert = sci_alert
        self.sci_cfg = sci_cfg
        self.hmi_alert = self.produce_alert(notice_str)

    def produce_alert(self, notice_str):
        obs_window = self.sci_alert.observation_window
        coords = self.sci_alert.coords
        sci_case_name = self.sci_cfg.name

        hmi_alert = "ALERT TO HMI:\n\n %s for the science config: %s\n" % (notice_str, sci_case_name)
        hmi_alert += "%s\n" % obs_window
        hmi_alert += "{}".format(coords)

        return hmi_alert


class SAG_notification:
    ''' class for notoficiations aimed at the SAG '''
    def __init__(self):
        pass


class STS_alert:
    ''' class  for alerts aimed at the STS '''
    def __init__(self):
        pass

class alert_summary:
    def __init__(self, followup_op):
        self.followup_op = followup_op
        self.sci_alert_summary = None
        self.sci_cfg_summaries = None
        self.cut_summary = None
        self.pointing_pattern_summary = None
        self.full_summary = None
        self.fill()

    def fill(self):
        alert_sum = sci_alert_summary(self.followup_op)
        self.sci_alert_summary = alert_sum.summary
        self.cut_summary = str(self.followup_op.science_config.cut_collection)

        self.sci_cfg_summary = self.followup_op.science_config.get_summary()

        pattern_summary = pointing_summary(self.followup_op)
        self.pointing_pattern_summary = pattern_summary.summary

        # pattern possible? Duration > 0
        duration = self.followup_op.science_config.observation_window.duration
        if duration:
            self.poiing_pattern_summary = pointing_summary(self.followup_op)

        header = "#" * 20 + "\n"
        header += "ALERT SUMMARY:\n"
        header += "  " + self.followup_op.science_config.name
        header += " - " + self.followup_op.science_alert.ivorn
        header += "\n"

        self.full_summary = header
        self.full_summary += "\nScience Alert Sumary:\n" + self.sci_alert_summary
        self.full_summary += "\nScience Config Details:\n" + self.sci_cfg_summary
        self.full_summary += "\nSuggested Pointing Pattern:\n" + self.pointing_pattern_summary
        self.full_summary += "\nCut Summary:\n" + self.cut_summary

        self.full_summary += "#" * 20 + "\n"


class sci_alert_summary:
    def __init__(self, followup_opp):
        alert = followup_opp.science_alert
        coord = "RA: {} deg, Dec: {} deg, Err: {} deg".format(alert.coords.ra,
                                                              alert.coords.dec,
                                                              alert.coords.err)
        summ = ""
        summ += "{}\n".format("Processed alert:")
        summ += "{: <20}  {}\n".format("Unique ID:", alert.ivorn)
        summ += "{: <20}  {}\n".format("Coordinates:", coord)
        summ += "{: <20}  {}\n".format("Event Time:", alert.event_time)
        summ += "{: <20}  {}\n".format("Received Time:", alert.alert_received_time)

        self.summary = summ


class pointing_summary:
    def __init__(self, match):
        if match.science_config.pointing_pattern:
            summary = "Pointing Pattern:\n"
            summary += "{: <15} | {: <15} | {: <15}\n".format("RA (deg)", "Dec (deg)", "Exposure")
            summary += match.science_config.pointing_pattern.get_summary()
            self.summary = summary
        else:
            self.summary = "No Suggestion\n"

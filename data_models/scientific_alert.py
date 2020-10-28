# definition of scientific alert that is used troughout the Transients Handler
# can be created from external scientific (voevent) alerts as well as from
# SAG alerts.

import voeventparse as vp
from datetime import datetime


class InjectVoeventSciAlertFactory:
    def generate_scientific_alert(self, voevent_path):
        sci_alert = ScientificAlert()
        with open(voevent_path, 'rb') as file:
            voevent = vp.load(file)
        sci_alert.from_voevent(voevent)
        return sci_alert


class CometVoeventSciAlertFactory:
    def generate_scientific_alert(self, voevent):
        sci_alert = ScientificAlert()
        sci_alert.from_voevent(voevent)
        return sci_alert


class SAGSciAlertFactory:
    def generate_scientific_alert(self, sag_alert):
        sci_alert = ScientificAlert()
        sci_alert._from_sag_alert(sag_alert)
        return sci_alert


class SUSSSciAlertFactory:
    def generate_scientific_alert(self, suss_alert):
        sci_alert = ScientificAlert()
        sci_alert._from_suss_alert(suss_alert)
        return sci_alert


class ScientificAlertFactory:
    def __init__(self, sci_alert_factory, received_alert):
        self.factory = sci_alert_factory
        self.sci_alert = self.factory.generate_scientific_alert(received_alert)


class ScientificAlert:
    def __init__(self):
        # origin parameters
        self.is_external = False
        self.is_internal_sag = False
        self.is_internal_suss = False

        # core parameters from external events
        self.ivorn = None
        self.author = None
        self.alert = None
        self.coords = None
        self.event_time = None
        self.alert_received_time = None
        self.alert_authored_time = None

        # most of the neede configurational parameters
        self.processing_cases = None
        self.testing_conditions_applied = False
        self.observation_window = None

        # optional parameters that may be used
        self.custom_observation_coordinates = []

    def from_voevent(self, voevent):
        self.alert = voevent
        self.is_voevent = True
        self.ivorn = voevent.attrib['ivorn']
        self.coords = vp.get_event_position(voevent)
        self.event_time = vp.convenience.get_event_time_as_utc(voevent).replace(tzinfo=None)
        self.alert_received_time = datetime.utcnow().replace(tzinfo=None)
        self.alert_authored_time = voevent['Who']['Date']
        self.author = voevent['Who']['Author']['shortName']

    def register_processing_results(self):
        pass

    def _from_sag_alert(self, sag_alert):
        # Need to know interface
        pass

    def _from_suss_alert(self, suss_alert):
        # Need to know interface
        pass

    def __str__(self):
        out = "ALERT SUMMARY:\n"
        out_map = {}
        if self.is_voevent:
            out_map = {"ivorn": self.ivorn,
                       "author": self.author,
                       "alert authored time": self.alert_authored_time,
                       "alert received time": self.alert_received_time,
                       "coordinates": self.coords,
                       "event time": self.event_time,
                       "test conditions": self.testing_conditions_applied}

        for name, val in out_map.items():
            out += "{: <30}: {}\n".format(name, val)
        return out

    def archive_sci_alert(self):
        # Needs DB api
        pass

    def update_archived_alert(self):
        # Needs DB api
        pass

    def query_nearby_preceeding_alerts(self, search_radius, time_range):
        # needs DB and/or api (will try voeventdb.remote for mini-acada)
        pass

    def query_nearby_known_sources(self, search_radius):
        # needs catalogue infrastructure
        pass

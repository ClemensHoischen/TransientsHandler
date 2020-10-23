''' plugin for comet that initiates the processing by the Transients Handler.

To be installed within Comet (link to Comet/comet/plugins/)

enabled using the --th_entry. using --th_entry-allowed-types, different alert types
can be alloed for processing.

Example:

-- th_entry-allowed-types Swift,BAT_GRB_Pos++Fermi,LAT_Offline_Pos

allowed will be alerts with an ivorn in which either Swift AND BAT_GRB_Pos OR
Fermi AND Offline_Pos occurs.
'''

import sys

from zope.interface import implementer
from twisted.plugin import IPlugin

from comet.icomet import IHandler, IHasOptions
import comet.log as log

sys.path.append("/Users/hoischen/CTA/TransientsHandler")
from broker_system import entry_points


@implementer(IPlugin, IHandler, IHasOptions)
class TH_Entry(object):
    name = "th_entry"

    def __init__(self):
        self.allowed_types = []

    def __call__(self, event):
        self.ivorn = event.element.attrib['ivorn']
        log.debug("TH_ENTRY CHECKING: %s" % self.ivorn)
        allowed_checks = []
        for allowed in self.allowed_types:
            all_ids_found = True
            log.debug("   - Testing: %s" % allowed)
            for a in allowed:
                if a not in self.ivorn:
                    all_ids_found = False
            allowed_checks.append(all_ids_found)

        if True in allowed_checks:
            self.start_processing(event)
        else:
            log.debug("%s is not allowed for the TH." % self.ivorn)

    def start_processing(self, event):
        comet_origin = entry_points.alert_origin.comet_voevent
        entry_points.alert_entry(event, comet_origin)
        log.debug("PROCESSING OF %s initiated..." % self.ivorn)

    def get_options(self):
        return [('allow-types', self.allowed_types,
                 'option that specifies an allowed alert type.\nexpects something like SWIFT,BAT_GRB_Pos++Fermi,LAT_Offline\"')]

    def set_option(self, name, value):

        log.debug("OPTION: NAME: %s, VALUE: %s" % (name, value))
        if name == 'allow-types':
            individual_types = value.split("++")
            for a_type in individual_types:
                self.allowed_types.append(a_type.split(","))


# This instance of the handler is what actually constitutes our plugin.
th_entry = TH_Entry()

'''
Processing manager module.
This module handles the different processing steps of:
- matching science cases and the alert
- initiation of the core processing
- finalization after the core processing (e.g. reporting and communication)
'''

import communicator.communicator as cmn

import astropy.units as u
from astropy.units import Quantity


from alert_processor import observation_windows
from utilities.observatories import CTA_North
from astropy import units as u


# copied here from core_processing
def find_observation_window(sci_alert, case,
                            custom_ra=None, custom_dec=None, custom_unit=None, custom_time=None):
    ra = sci_alert.coords.ra * u.Unit(sci_alert.coords.units)
    dec = sci_alert.coords.dec * u.Unit(sci_alert.coords.units)
    time = sci_alert.alert_received_time

    # allow to overwrite the coordinates and time in order to enable
    # search for complex tiling patterns
    if custom_ra and custom_dec and custom_time:
        ra = custom_ra
        dec = custom_dec
        time = custom_time

    obs_window_reqs = case.obsevation_window_reqs
    obs_window = observation_windows.ObservationWindow(ra, dec, time,
                                                       CTA_North(), obs_window_reqs)
    valid_window = obs_window.find_observation_window(time.replace(tzinfo=None))
    if not valid_window:
        print("No valid observation window found. Continuing!")

    # print(obs_window)

    return obs_window

# copied here from core_processing
def process_cases(sci_alert, science_case):

    print("\n -------------")
    print("  HANDLING: %s" % science_case.name)
    print(" -------------- \n")

    valid_window = find_observation_window(sci_alert, science_case)
    science_case.observation_window = valid_window

    # apply cuts
    print("CUTS:")

    science_case.cut_collection.execute(sci_alert, valid_window, science_case)

    all_applied_cuts_results = science_case.cut_collection.result()

    if all_applied_cuts_results is False:
        print("  --> Not all cuts passed. -> No action.")
    else:
        print("  --> All cuts passed. -> Initiating further actions.")




class processing_manager:
    ''' core class of the processing manager holding the configurations and
    the matches of science cases and the alert.
    '''
    def __init__(self, science_configs, site_config):
        self.science_config = science_configs
        self.site_config = site_config
        self.communicator = None
        self.matches = None

    def process(self, sci_alert, communicator):
        self.communicator = communicator

        self.initiate_processing(sci_alert)
        self.core_processing()
        self.finalize_processing()

    def initiate_processing(self, science_alert):
        # search matching science configs
        matches = match_science_configurations(science_alert, self.science_config)
        # start processing in parallel
        sorted_matches = sorted(matches, key=lambda matches: matches.science_config.observation_config.priority,
                                reverse=True)
        self.matches = sorted_matches
        self.communicator.register_all_matches(self.matches)

        for match in self.matches:
            if match.science_config.notification_opts.any_on_received():
                # do this in parallel to the main process_cases task.
                self.communicator.communicate_received(match)

    def core_processing(self):
        for match in self.matches:
            process_cases(match.science_alert, match.science_config)

    def finalize_processing(self):
        accepted_matches = []
        for match in self.matches:
            match.report()
            match.update_archive()
            if match.pair_accepted():
                print("%s  -->  Needs to be communicated" % match.science_config.name)
                accepted_matches.append(match)

        self.communicator.register_accepted_matches(accepted_matches)

        print("Number of accepted matches: %i of %i" % (len(accepted_matches),
                                                        len(self.matches)))

        for match in accepted_matches:
            if match.science_config.notification_opts.any_on_accepted():
                match.science_config.pointing_pattern = produce_pointing_pattern(match.science_config)

    def validate_test_case(self):
        pass


def produce_pointing_pattern(sci_case):
    # do some checks, that all all needed data is there.
    pattern = pointing_pattern()
    max_exposure = sci_case.observation_config.exposure
    number_blocks = sci_case.observation_config.number_blocks
    window_duration = sci_case.observation_window.duration
    if not window_duration:
        return None

    wobble_offset = Quantity("0.5 deg")  # Quantity(sci_case.observation_config.pointing_mode.obs_type.offset)
    ra = sci_case.observation_window.ra
    dec = sci_case.observation_window.dec

    duration = min([window_duration, max_exposure])
    print(duration, type(duration))
    exposure_per_block = duration / number_blocks
    ra_offsets, dec_offsets = generate_wobble_offsets(number_blocks, wobble_offset)

    for i in range(number_blocks):
        block = observation_block(ra, ra_offsets[i], dec, dec_offsets[i], exposure_per_block)
        pattern.add_block(block)

    return pattern


def generate_wobble_offsets(number_blocks, offset):
    ra_offsets = []
    dec_offsets = []
    i = 0
    while i < number_blocks:
        if round(i / 2):
            dec_off = offset
            ra_off = 0
        else:
            dec_off = 0
            ra_off = offset

        ra_offsets.append(ra_off)
        dec_offsets.append(dec_off)
        i += 1

    return ra_offsets, dec_offsets


def match_science_configurations(science_alert, science_configs):
    ''' function that matches the science alert to science configs '''
    print("Matching Science configs...")
    ivorn = science_alert.ivorn
    matches = []

    for sci_case in science_configs:
        for allowed_type in sci_case.allowed_alert_types:
            if allowed_type.alert_type in ivorn:
                pair = alert_science_config_pair(science_alert, sci_case)
                matches.append(pair)

    print("Found Matching science configurations:")
    for match in matches:
        print(match)

    return matches


class alert_science_config_pair:
    ''' container class for matching alerts and science configs. '''
    # TODO: change to follow-up opportunity
    def __init__(self, alert, config):
        self.science_alert = alert
        self.science_config = config
        self.summary = None

    def report(self):
        out = "--" * 10 + "\n"
        out += "REPORT:\n"
        out += self.science_alert.ivorn + " <-> "
        out += self.science_config.name + "\n"
        out += "--" * 10 + "\n"
        out += str(self.science_config.cut_collection)

        print(out)

        # print("Report # TO BE IMPLEMENTED")

    def passed_all(self):
        passed_cuts = self.science_config.cut_collection.result()
        return passed_cuts

    def update_archive(self):
        pass

    def pair_accepted(self):
        if self.passed_all():
            return True
        else:
            return False

    def __str__(self):
        out = "%s - %s" % (self.science_alert.ivorn, self.science_config.name)
        return out


# TDODO: migrate pointing_pattern and observation_block to appropriate class

class pointing_pattern:
    def __init__(self):
        self.observation_blocks = []

    def add_block(self, block):
        self.observation_blocks.append(block)

    def get_summary(self):
        out = ""
        for block in self.observation_blocks:
            out += block.get_summary() + "\n"

        return out


class observation_block:
    def __init__(self, ra, d_ra, dec, d_dec, exposure):
        self.target_ra = None
        self.target_dec = None
        self.target_exposure = None

        self.set(ra, d_ra, dec, d_dec, exposure)

    def set(self, ra, d_ra, dec, d_dec, exposure):
        self.target_ra = ra + d_ra
        self.target_dec = dec + d_dec
        self.target_exposure = exposure

    def get_summary(self):
        if self.target_exposure == 0:
            return "No Window!"

        out = "{: <15.2f} | {: <15.2f} | ".format(self.target_ra / u.deg,
                                                  self.target_dec / u.deg)
        out += "{0.value:0.02f} {0.unit:s}".format(self.target_exposure.to("min"))
        return out

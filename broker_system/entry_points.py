from alert_processor import processing_manager

from data_models import site_config
# from parsers import site_config_parser as site_cfg_parser
from data_models.scientific_alert import scientific_alert_factory as saf
from data_models.scientific_alert import inject_voevent_sci_alert_factory as inj_voevent_saf
from data_models.scientific_alert import comet_voevent_sci_alert_factory as comet_voevent_saf
from data_models.scientific_alert import sag_sci_alert_factory as sag_saf
from data_models.scientific_alert import suss_sci_alert_factory as suss_saf
from data_models.science_config import science_configuration

import communicator.communicator as comm

from broker_system import alert_verifyer
import os
from enum import Enum

g_site_cfg_path = '/Users/hoischen/CTA/TransientsHandler/configurations/site_config.json'


def setup_site_cfg():
    site_cfg = site_config.site_configuration()
    site_cfg.read_site_cfg(g_site_cfg_path)  # Query from DB later
    return site_cfg


def setup_science_cfgs(site_cfg):
    science_cfg_path = site_cfg.science_config_paths
    cfgs = os.listdir(science_cfg_path)
    cfgs = [science_cfg_path + "/" + cfg for cfg in cfgs]

    science_cfgs = []
    for cfg in cfgs:
        sci = science_configuration(cfg)
        print(sci)
        science_cfgs.append(sci)
    return science_cfgs


class alert_origin(Enum):
    # different origins of alerts according to interface list and use
    # cases, different extraction of information can occur.
    injected_voevent = "injected_voevent",
    comet_voevent = 'comet_voevent'
    sag_alert = 'sag_alert'
    suss_alert = 'suss_alert'


def factory_switch(origin):
    # Spefies the factory to generate the scientific alert from the input
    # alert
    switcher = {alert_origin.injected_voevent: inj_voevent_saf,
                alert_origin.comet_voevent: comet_voevent_saf,
                alert_origin.sag_alert: sag_saf,
                alert_origin.suss_alert: suss_saf}
    func = switcher.get(origin)
    return func()


def alert_entry(alert, origin, test_conditions=None):
    print("Received alert of origin: %s" % origin)

    site_cfg = setup_site_cfg()
    science_cfgs = setup_science_cfgs(site_cfg)

    allowed_alert_types = site_cfg.allowed_alert_types
    proc_manager = processing_manager.processing_manager(science_cfgs, site_cfg)

    factory = factory_switch(origin)
    sci_alert_factory = saf(factory, alert)
    sci_alert = sci_alert_factory.sci_alert
    if test_conditions:
        test_conditions.apply_test_conditions_to_scientific_alert(sci_alert)

    alert_allowed = alert_verifyer.verify_alert(sci_alert, allowed_alert_types)
    if not alert_allowed:
        print("Alert is not valid to be processed by the TH. Aborting!")
        # Do clean-up

    print("Alert is valid and processing is initiated...")

    communicator = comm.communicator()

    proc_manager.process(sci_alert, communicator)

    communicator.communicate_results()

    if test_conditions:
        proc_manager.validate_test_case()
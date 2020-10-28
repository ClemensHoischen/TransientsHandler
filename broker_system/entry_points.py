from alert_processor import processing_manager

from data_models import site_config
# from parsers import site_config_parser as site_cfg_parser
from data_models.scientific_alert import ScientificAlertFactory as saf
from data_models.scientific_alert import InjectVoeventSciAlertFactory as inj_voevent_saf
from data_models.scientific_alert import CometVoeventSciAlertFactory as comet_voevent_saf
from data_models.scientific_alert import SAGSciAlertFactory as sag_saf
from data_models.scientific_alert import SUSSSciAlertFactory as suss_saf
from data_models.science_config import ScienceConfiguration

import communicator.communicator as comm

from broker_system import alert_verifyer
import os
from enum import Enum



def setup_site_cfg():
    site_cfg = site_config.SiteConfiguration()
    site_cfg.read_site_cfg(os.environ['TH_site_config'])  # Query from DB later
    return site_cfg


def setup_science_cfgs(site_cfg):
    science_cfg_path = site_cfg.science_config_paths
    cfgs = os.listdir(science_cfg_path)
    cfgs = [science_cfg_path + "/" + cfg for cfg in cfgs]

    science_cfgs = []
    for cfg in cfgs:
        sci = ScienceConfiguration(cfg)
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
    proc_manager = processing_manager.ProcessingManager(science_cfgs, site_cfg)

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

    communicator = comm.Communicator()

    proc_manager.process(sci_alert, communicator)

    communicator.communicate_results()

    if test_conditions:
        proc_manager.validate_test_case()
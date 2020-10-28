'''
module containg the site configuration and the parsing functions
'''

import json


class SiteConfiguration:
    ''' main class containing the site configuration info '''
    def __init__(self):
        self.site_cfg_path = None
        self.state = None
        self.site = None
        self.science_config_paths = None
        self.allowed_alert_types = []

    def read_site_cfg(self, site_cfg_path):
        ''' reads the actual site config file '''
        self.site_cfg_path = site_cfg_path
        with open(site_cfg_path, "r") as read_file:
            data = json.load(read_file)

        print(data)
        self.science_config_paths = parse_science_config_paths(data)
        self.site = parse_site(data)
        self.allowed_alert_types = parse_allowed_alerts(data)

    def __str__(self):
        return ""

def parse_science_config_paths(data):
    ''' parses the path under which the science configurations are stored '''
    try:
        sci_conf_path = data['SiteConfig']["science_config_path"]
        return sci_conf_path
    except Exception:
        print("Unable to read the science config path.")

    return None

def parse_allowed_alerts(data):
    ''' parses the alerts which are allowed to be processed '''
    try:
        allowed_alerts = data['SiteConfig']['allowed_alerts']
        return allowed_alerts
    except Exception:
        print("Unable to read the allowed alerts.")

    return None

def parse_site(data):
    ''' parses the site specified in the site config '''
    try:
        site = data['SiteConfig']["site"]
        return site
    except Exception:
        print("Unable to read the site.")

    return None

import json


class SiteConfiguration:
    def __init__(self):
        self.site_cfg_path = None
        self.state = None
        self.site = None
        self.science_config_paths = None
        self.allowed_alert_types = []

    def read_site_cfg(self, site_cfg_path):
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
    try:
        sci_conf_path = data['SiteConfig']["science_config_path"]
        return sci_conf_path
    except Exception:
        print("Unable to read the science config path.")
    
    return None

def parse_allowed_alerts(data):
    try:
        allowed_alerts = data['SiteConfig']['allowed_alerts']
        return allowed_alerts
    except Exception:
        print("Unable to read the allowed alerts.")
    
    return None

def parse_site(data):
    try: 
        site = data['SiteConfig']["site"]
        return site
    except Exception:
        print("Unable to read the site.")
    
    return None
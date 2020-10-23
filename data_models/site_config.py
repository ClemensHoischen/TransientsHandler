import json

from parsers import site_config_parser as scp


class site_configuration:
    def __init__(self):
        self.site_cfg_path = None
        self.state = None
        self.site = None
        self.connected_systems = None  # from interfaces module
        self.science_config_paths = None
        self.allowed_alert_types = []

    def read_site_cfg(self, site_cfg_path):
        print(site_cfg_path)
        self.site_cfg_path = site_cfg_path
        with open(site_cfg_path, "r") as read_file:
            data = json.load(read_file)

        print(data)
        self.connected_systems = scp.parse_connected_systems(data)
        self.science_config_paths = scp.parse_science_config_paths(data)
        self.site = scp.parse_site(data)
        self.allowed_alert_types = scp.parse_allowed_alerts(data)

    def __str__(self):
        return ""

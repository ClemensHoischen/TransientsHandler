

def parse_science_config_paths(data):
    sci_conf_path = data['SiteConfig']["science_config_path"]
    print(sci_conf_path)
    return sci_conf_path


def parse_allowed_alerts(data):
    allowed_alerts = data['SiteConfig']['allowed_alerts']
    print(allowed_alerts)
    return allowed_alerts


def parse_site(data):
    pass


def parse_connected_systems(data):
    pass

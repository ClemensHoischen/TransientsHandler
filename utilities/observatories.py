from astropy import units as u
from astropy.coordinates import EarthLocation

# TODO: use correct height
class CTANorth:
    def __init__(self):
        self.lat = 17.89 * u.deg
        self.lon = 28.75 * u.deg
        self.height = 2000 * u.m
        self.location = EarthLocation(lat=self.lat, lon=self.lon,
                                      height=self.height)
        self.name = "CTA North"

# TODO: use correct height
class CTASouth:
    def __init__(self):
        self.lat = -24.68 * u.deg
        self.lon = 70.32 * u.deg
        self.height = 1835 * u.m
        self.location = EarthLocation(lat=self.lat, lon=self.lon,
                                      height=self.height)
        self.name = "CTA South"

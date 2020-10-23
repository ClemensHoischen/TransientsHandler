from astropy import units as u
from astropy.coordinates import EarthLocation


class HESSObservatory:
    def __init__(self):
        self.Lat = -23.271778 * u.deg
        self.Lon = 16.50022 * u.deg
        self.Height = 1835 * u.m
        self.Location = EarthLocation(lat=self.Lat, lon=self.Lon,
                                      height=self.Height)


# TODO: use correct height
class CTA_North:
    def __init__(self):
        self.Lat = 17.89 * u.deg
        self.Lon = 28.75 * u.deg
        self.Height = 2000 * u.m
        self.Location = EarthLocation(lat=self.Lat, lon=self.Lon,
                                      height=self.Height)

# TODO: use correct height
class CTA_South:
    def __init__(self):
        self.Lat = -24.68 * u.deg
        self.Lon = 70.32 * u.deg
        self.Height = 1835 * u.m
        self.Location = EarthLocation(lat=self.Lat, lon=self.Lon,
                                      height=self.Height)

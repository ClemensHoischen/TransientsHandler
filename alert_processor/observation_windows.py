'''
ObservationWindow Module

This module takes care of all calculations needed to find a range of time
during which all observability criteria (e.g. zenith constraints and sky brightness)
are fulfilled. the observability criteria are taken from the science configurations
which are currently being evaluated by the TH alerter.

'''

from datetime import datetime

import numpy as np
import ephem

from astropy import units as u
from astropy.units import Quantity
from astropy.time import Time
from astropy.coordinates import SkyCoord, AltAz, FK5, Angle
from astropy.coordinates import get_sun

from matplotlib.dates import num2date, date2num

from utilities import observatories

gSunDown = -18.0 * u.deg
gMoonDown = -0.5 * u.deg


def radec_from_altaztime(alt, az, time, site):
    ''' converts ra dec coordinates to alt az at a given time and site location'''
    alt_az = AltAz(alt=Angle(float(alt), unit=u.deg),
                   az=Angle(float(az), unit=u.deg),
                   location=site.location,
                   obsTime=Time(time))
    ra_dec = alt_az.transform_to(FK5(equinox='J2000'))
    return ra_dec.ra / u.deg, ra_dec.dec / u.deg


def is_darkness(sunAlt, moonAlt):
    ''' checks the darkness definition
    TODO: implement different darkness definition that are
    part of the site configuration, rather than global values.
    This shall include moon conditions '''
    if sunAlt > gSunDown:
        return False
    if moonAlt > gMoonDown:
        return False

    # print sunAlt, moonAlt
    return True


def source_alt(obs_time, ra, dec, site):
    ''' calculates the altitude of a source at time 'obs_time' at location 'site' '''
    position = SkyCoord(ra, dec, unit=u.deg)
    alert_time = Time(obs_time)
    source_alt_az = position.transform_to(AltAz(obstime=alert_time,
                                                location=site.location))
    return source_alt_az.alt / u.deg


def source_az(obs_time, ra, dec, site):
    ''' calculates the azimuth of a source at time 'obs_time' at location 'site' '''
    position = SkyCoord(ra, dec, unit=u.deg)
    alert_time = Time(obs_time)
    source_alt_az = position.transform_to(AltAz(obstime=alert_time,
                                                location=site.location))
    return source_alt_az.az / u.deg


def sun_alt(obs_time, site):
    ''' calculates the altitude of the sun at time 'obs_time' at location 'site' '''
    sun = get_sun(Time(obs_time)).transform_to(AltAz(obstime=Time(obs_time),
                                                     location=site.location))
    return sun.alt / u.deg


def moon_alt(obs_time, site):
    ''' calculates the altitude of the moon at time 'obs_time' at location 'site' '''
    moon = ephem.Moon()
    obs = ephem.Observer()
    obs.lon = str(site.lon / u.deg)
    obs.lat = str(site.lat / u.deg)
    obs.elev = site.height / u.m
    obs.date = obs_time
    moon.compute(obs)

    # print "Altitude of the Moon = %s deg" % (moon.alt * 180. / np.pi)

    return moon.alt * 180. / np.pi


def moon_phase(obs_time, site):
    ''' calculates moon phase in percent at time 'obs_time' at location 'site' '''
    moon = ephem.Moon()
    obs = ephem.Observer()
    obs.lon = str(site.lon / u.deg)
    obs.lat = str(site.lat / u.deg)
    obs.elev = site.height / u.m
    obs.date = obs_time
    moon.compute(obs)

    # print "Phase of the moon = %s percent" % moon.phase

    return moon.phase


def moon_az(obs_time, site):
    ''' calculates the moons azimuth at time 'obs_time' at location 'site' '''
    moon = ephem.Moon()
    obs = ephem.Observer()
    obs.lon = str(site.lon / u.deg)
    obs.lat = str(site.lat / u.deg)
    obs.elev = site.height / u.m
    obs.date = obs_time
    moon.compute(obs)

    return moon.az * 180 / np.pi


def moon_dist(obs_time, ra, dec, site):
    ''' calculates the angular distance between the moon and a
        target at ra, dec at time 'obs_time' at location 'site' '''
    a_moon_alt = Angle(moon_alt(obs_time, site) * u.deg, unit=u.deg)
    a_moon_az = Angle(moon_az(obs_time, site) * u.deg, unit=u.deg)
    a_source_alt = Angle(source_alt(obs_time, ra, dec, site) * u.deg, unit=u.deg)
    a_source_az = Angle(source_az(obs_time, ra, dec, site) * u.deg, unit=u.deg)

    a_source_altaz = AltAz(alt=a_source_alt, az=a_source_az, location=site.location, obstime=obs_time)
    a_moon_altaz = AltAz(alt=a_moon_alt, az=a_moon_az, location=site.location, obstime=obs_time)
    a_moon_sep = a_moon_altaz.separation(a_source_altaz)

    # print "Distance between source and moon = %s deg" % (moon_sep.deg)

    return a_moon_sep


class ObservationWindow:
    ''' Class that holds the information of observation windows for a
        given target with coordinates ra, dec.

        Main functions are:
         * Reading observability criteria from the science config
           (from the obs_window_cfg object)
         * Calculating the sun, source and moon altitude/azimuth profiles along a
           time window (calculate_source_sun_moon())
         * Calculating the observation window parameters for the given criteria,
           resulting in delay, start time, end time and duration of the window.
    '''

    def __init__(self, ra=None, dec=None, event_time=None, observatory_site=None, obs_window_cfg=None):
        ''' initialization of an ObservationWindow object.
            Can be initialized without any parameters to make dynamic use of the core
            functions in common and custom cuts implemented in the transients handler.
        '''
        self.ra = ra
        self.dec = dec

        self.event_time = event_time
        if not self.event_time:
            self.event_time = datetime.utcnow()

        self.site = observatory_site
        if not self.site:
            self.site = observatories.CTANorth

        if obs_window_cfg:
            self.source_zenith_max = obs_window_cfg.max_zenith_angle
            self.source_alt_limit = 90 * u.deg - self.source_zenith_max
            self.max_delay = obs_window_cfg.max_delay_to_event
            self.min_duration = obs_window_cfg.min_window_duration
            # ToBeUsed
            self.min_nsb = obs_window_cfg.min_nsb
            self.max_nsb = obs_window_cfg.max_nsb
            self.illumination = obs_window_cfg.illumination
            self.test_dates = self.setup_time_window_search()

        # Filled by CalculateSourceSunMoon()
        self.sun_alts = None
        self.moon_alts = None
        self.source_alts = None
        if self.ra and self.dec:
            self.calculate_source_sun_moon()

        # filled by FindObservationWindow()
        self.delay = np.Inf
        self.start = None
        self.end = None
        self.duration = 0
        self.all_valid_times = None

    def __str__(self):
        ''' formatted output of the observation window final values '''
        if self.all_valid_times is not None:
            out = "\nOBSERVATION WINDOW:\n"
            out += "{: <30} : {:.2f}, {:.2f}\n".format("  * Ra, Dec", self.ra, self.dec)
            out += "{: <30} : {:.2f}\n".format("  * delay", self.delay)
            out += "{: <30} : {}\n".format("  * start time", self.start)
            out += "{: <30} : {}\n".format("  * end time", self.end)
            out += "{: <30} : {:.2f}\n".format("  * duration", self.duration)
            return out

        return "\n NO OBSERVATION WINDOW FOUND!\n"

    def setup_time_window_search(self):
        ''' prepares the grid of times where the observation window will be searched in.
        The range varies depending on the maximum allowed delay time. '''
        self.time_range_to_test = [-0.2 * self.max_delay, +1.5 * self.max_delay]
        total_range_hours = self.time_range_to_test[1] - self.time_range_to_test[0]
        n_steps = np.minimum(500, int(total_range_hours.value) * 25)

        centerdate = Time(datetime(self.event_time.year, self.event_time.month,
                                   self.event_time.day, self.event_time.hour))

        time_range = np.linspace(self.time_range_to_test[0].value,
                                 self.time_range_to_test[1].value,
                                 n_steps)

        self.test_times = centerdate + time_range * u.hour
        self.test_dates = None
        try:
            self.test_dates = np.array([date2num(x.datetime) for x in self.test_times])
        except Exception as x:
            print(x)

        return self.test_dates

    def calculate_source_sun_moon(self):
        ''' caluclates the altitude profiles along the time range for the observation window search
        for the source position, moon and sun '''
        ra = self.ra
        dec = self.dec

        position = SkyCoord(ra.value, dec.value, unit=ra.unit)
        # print(position)

        altaz_frame = AltAz(obstime=self.test_times, location=self.site.location)
        sun_alt_azs = get_sun(self.test_times).transform_to(altaz_frame)
        source_alt_az = position.transform_to(AltAz(obstime=self.test_times,
                                                    location=self.site.location))

        moon = ephem.Moon()
        obs = ephem.Observer()
        obs.lon = str(self.site.lon / u.deg)
        obs.lat = str(self.site.lat / u.deg)
        obs.elev = self.site.height / u.m

        moon_alts = np.zeros_like(self.test_dates)
        moon_azs = np.zeros_like(self.test_dates)
        moon_phase = np.zeros_like(self.test_dates)

        for ii, tt in enumerate(self.test_times):
            obs.date = ephem.Date(tt.datetime)
            moon.compute(obs)
            moon_alts[ii] = moon.alt * 180. / np.pi
            moon_azs[ii] = moon.az * 180. / np.pi
            moon_phase[ii] = moon.phase

        moon_alt_az = AltAz(alt=Angle(moon_alts, unit=u.deg),
                            az=Angle(moon_azs, unit=u.deg),
                            location=self.site.location, obstime=self.test_times)

        # store information for plotting
        self.sun_alts = sun_alt_azs.alt
        self.source_alts = source_alt_az.alt
        self.moon_alts = moon_alt_az.alt

    def find_observation_window(self, now):
        ''' actual application of the visibility constraints given by the science config at
        time 'now' '''

        sun_mask = self.sun_alts < gSunDown
        moon_mask = self.moon_alts < gMoonDown
        source_mask = self.source_alts > self.source_alt_limit
        all_masks = sun_mask & moon_mask & source_mask
        valid_dates = self.test_dates[all_masks]

        good_obs_times = [num2date(d) for d in valid_dates]

        if len(good_obs_times) is 0:
            # print "No observation Window found!"
            # print("No observation Window in darktime found!")
            return False

        ar_obstimes = np.array([o.replace(tzinfo=None) for o in good_obs_times])
        future = ar_obstimes > now
        fut_obstimes = ar_obstimes[future]

        if len(fut_obstimes) is 0:
            print("no observation window > alert time in darktime")
            return False

        fut_window = fut_obstimes

        # get delay, start and end time of the window
        obs_delay = round((fut_window[0] - self.event_time).total_seconds() / 60. / 60., 3)
        self.delay = Quantity(obs_delay * u.hour)
        start_time = fut_window[0].replace(tzinfo=None)
        self.start = start_time
        end_time = fut_window[-1].replace(tzinfo=None)
        self.end = end_time

        for i in range(len(fut_obstimes) - 1):
            delta = (fut_window[i + 1] - fut_window[i]).total_seconds()
            if delta > 1. * 60. * 60.:
                end_time = fut_window[i].replace(tzinfo=None)
                break

        obs_dur = (end_time - start_time).total_seconds() / 60. / 60.
        self.duration = Quantity(obs_dur * u.hour)
        self.all_valid_times = fut_window

        return True

    def test(self, ra, dec, time, site,
             zenith_max, max_delay, min_duration, allowed_brightness,
             expected_delay, expected_start, expected_end, expected_duration):
        ''' testing function that replicates the core function of the
            ObservationWindow class.  The calculated ObservationWindow
            results are compared to expected results for unit testing. '''

        self.ra = ra
        self.dec = dec
        self.event_time = time
        self.site = site

        self.source_zenith_max = zenith_max
        self.source_alt_limit = 90 * u.deg - self.source_zenith_max
        self.max_delay = max_delay
        self.min_duration = min_duration
        # self.allowed_sky_brightness = None  # allowed_brightness  # not used currently

        print("OBS WINDOW UNITTEST")
        self.test_dates = self.setup_time_window_search()
        self.calculate_source_sun_moon()
        self.find_observation_window(self.event_time)

        # final values to be compared to expectation
        delay_ok = True
        start_ok = True
        end_ok = True
        duration_ok = True

        if not expected_delay - self.delay < (1 * u.s):
            print("ObservationWindowTest: Delay of the found window is incorrect!")
            print("... Got:", self.delay, "Expected:", expected_delay)
            delay_ok = False
        if not (expected_start - self.start).total_seconds() < 2:
            print((expected_start - self.start).total_seconds())
            print("ObservationWindowTest: Start Time of the found window is incorrect!")
            print("... Got:", self.start, "Expected:", expected_start)
            start_ok = False
        if not (expected_end - self.end).total_seconds() < 2:
            print((expected_end - self.end).total_seconds())
            print("ObservationWindowTest: End Time of the found window is incorrect!")
            print("... Got:", self.end, "Expected:", expected_end)
            end_ok = False
        if not abs(expected_duration - self.duration) < (2 * u.s):
            print("ObservationWindowTest: Duration of the found window is incorrect!")
            print("... Got:", self.duration, "Expected:", expected_duration)
            duration_ok = False

        test_results = [delay_ok, start_ok, end_ok, duration_ok]

        if False in test_results:
            print("ObservationWindowTest: Failed!")
            return False

        print("ObservationWindowTest: all tests passed.")
        return True

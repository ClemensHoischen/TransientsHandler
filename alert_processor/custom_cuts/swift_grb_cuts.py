from enum import Enum
import voeventparse

from astropy import units as u
from astropy.coordinates import SkyCoord

from datetime import timedelta
import processing.core_processing as cp


class custom_cuts_list(Enum):
    GRB_selection = "GRB_selection"
    Swift_counts = "Swift_counts"
    Custom_wobble = "Custom_coords"


def do_custom_cut(cut_id, sci_alert, sci_case, obs_window):
    if cut_id == custom_cuts_list.GRB_selection.value:
        alert_value = perform_grb_selection(sci_alert, sci_case, obs_window)
        return alert_value

    if cut_id == custom_cuts_list.Swift_counts.value:
        alert_value = get_swift_counts(sci_alert, sci_case, obs_window)
        return alert_value

    if cut_id == custom_cuts_list.Custom_wobble.value:
        alert_value = adjust_custom_coords(sci_alert, sci_case, obs_window)
        return alert_value


def perform_grb_selection(sci_alert, sci_case, obs_window):
    voevent = sci_alert.alert
    grouped_params = voeventparse.get_grouped_params(voevent)
    grb_identified = grouped_params['Solution_Status']['GRB_Identified']['value']

    return (grb_identified == "true")


def get_swift_counts(sci_alert, sci_case, obs_window):
    voevent = sci_alert.alert
    toplevel_params = voeventparse.get_toplevel_params(voevent)
    counts = toplevel_params["Burst_Inten"]["value"]
    return float(counts)


def adjust_custom_coords(sci_alert, sci_case, obs_window):
    ra = sci_alert.coords.ra
    dec = sci_alert.coords.dec

    good_custom_coords = []

    for i in range(0, 4):
        custom_ra = (ra + i * 0.1) * u.deg
        custom_dec = dec * u.deg
        custom_time = sci_alert.alert_received_time + timedelta(minutes=30)

        # search for observation window with the new coordinates
        custom_window = cp.find_observation_window(sci_alert, sci_case,
                                                   custom_ra=custom_ra,
                                                   custom_dec=custom_dec,
                                                   custom_time=custom_time)

        # check that the common cuts are still valid
        cut_collection = sci_case.cut_collection
        cut_collection.execute_common_cuts(sci_alert, custom_window, sci_case)

        if False in sci_case.cut_collection.common_cuts_results():
            # print(sci_case.cut_collection.report_common_cuts())
            continue
        else:
            coord = SkyCoord(ra=custom_ra, dec=custom_dec, frame='icrs')
            good_custom_coords.append(coord)
            print("custom wobble pos %i :" % (i + 1), coord)

    if len(good_custom_coords) == 4:
        sci_alert.custom_observation_coordinates = good_custom_coords
        return True
    else:
        return False

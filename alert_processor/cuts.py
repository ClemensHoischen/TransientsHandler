'''
Module that implemnets all needed funcionality for cuts.

Cuts are read from the science configurations and compiled
in CutCollections. Cuts are grouped in common and custom cuts.
common cuts are available for any alert out of the box.
custom cuts can be supplied by PIs if advanced processing is
necessary.
'''


from enum import Enum
import astropy.units as u
from astropy.units import Quantity
from numpy import inf

# import custom_cuts
import importlib
import voeventparse as vp


class Comparator(Enum):
    ''' comparing modes used to parse cuts from configs
     as well as for their exection '''
    greater = ">"
    less = "<"
    equal = "=="


class CutTypes(Enum):
    ''' types of cuts available '''
    common_cuts = "common"
    custom_cuts = "custom"


class CutCollection:
    ''' collection of all the cuts
     provides functions to register, report and execute the cuts '''
    def __init__(self, all_cut_data):
        ''' init function for the cut collection.
        registers all cuts that are supplied from the
        data extracted from the science config. '''
        self.all_cut_data = all_cut_data
        self.common_cuts = []
        self.custom_cuts = []
        self.register_cuts()

    def __str__(self):
        ''' print out of the cuts '''
        out = "Common cuts:\n"
        for cut in self.common_cuts:
            out += " %s\n" % cut
        out += "Custom cuts:\n"
        for cut in self.custom_cuts:
            out += " %s\n" % cut

        return out

    def register_cuts(self):
        ''' registration of cuts into the relevant category by extracting
        the cuts paramers name, comparison and required value.'''
        common_cuts_cfg = self.all_cut_data["CommonCuts"]
        for com_cut in common_cuts_cfg.items():
            name = com_cut[0]
            req = com_cut[1][0]
            comp = com_cut[1][1]
            self.register_cut(cut(name, req, comp, CutTypes.common_cuts))

        custom_cuts_cfg = self.all_cut_data['CustomCuts']
        for cust_cut in custom_cuts_cfg.items():
            # print(cust_cut[0].split(".")[1], " <-" * 5)
            name = cust_cut[0].split(".")[1]
            req = cust_cut[1][0]
            comp = cust_cut[1][1]
            origin = cust_cut[0].split(".")[0]
            self.register_cut(cut(name, req, comp, CutTypes.custom_cuts, origin))

    def register_cut(self, cut):
        ''' actual registration into common or custom cut list '''
        if cut.cut_type is CutTypes.common_cuts:
            self.common_cuts.append(cut)
        if cut.cut_type is CutTypes.custom_cuts:
            self.custom_cuts.append(cut)

    def execute(self, sci_alert, obs_window, sci_case):
        ''' execution of the cuts by applying the cuts with respect to
        the current science alert.

        looks up the correct cutstom cut module for custom cuts.'''
        for cut in self.common_cuts:
            cut.actual_value = determine_value(cut, sci_alert, obs_window)
            cut.evaluate()
            # print(cut)
        for cut in self.custom_cuts:
            custom_cut_module = importlib.import_module("alert_processor.custom_cuts." + cut.custom_origin)
            print(custom_cut_module)
            try:
                cut.actual_value = custom_cut_module.do_custom_cut(cut.cut_name, sci_alert,
                                                                   sci_case, obs_window)
                cut.evaluate()
                # print(cut)
            except Exception as excep:
                print("WARNING: Cut %s could not be executed: " % cut.cut_name, excep)
                cut._set_failed()
                # print(cut)

    def execute_common_cuts(self, sci_alert, obs_window, sci_case):
        ''' execution of common cuts '''
        for cut in self.common_cuts:
            cut.actual_value = determine_value(cut, sci_alert, obs_window)
            cut.evaluate()
            # print(cut)

    def common_cuts_results(self):
        ''' convenience to access the bulk results of common cuts. '''
        return [cut.passed for cut in self.common_cuts]

    def custom_cuts_results(self):
        ''' convenience function to access the bulk results of common cuts. '''
        return [cut.passed for cut in self.custom_cuts]

    def report_common_cuts(self):
        ''' compiles a report on the common cuts in string format '''
        rep = ""
        for cut in self.common_cuts:
            rep += str(cut.cut_name)
            rep += " -- cut passed: "
            rep += str(cut.passed)
            rep += "\n"
        return rep

    def report_custom_cuts(self):
        ''' compiles a report on the custom cuts in string format '''
        rep = ""
        for cut in self.custom_cuts:
            rep += str(cut.cut_name)
            rep += " -- cut passed: "
            rep += str(cut.passed)
            rep += "\n"
        return rep

    def result(self):
        ''' evaluation if all cuts have been passed and applied correctly '''
        all_passed_and_applied = True
        all_cuts = self.common_cuts + self.custom_cuts
        for cut in all_cuts:
            if not cut.performed:
                all_passed_and_applied = False
            if not cut.passed:
                all_passed_and_applied = False
        return all_passed_and_applied

    def report(self):
        ''' produces a general report '''
        return self.report_common_cuts() + self.report_custom_cuts()


def determine_value(cut, sci_alert, obs_window):
    ''' main function to determine the correct value depending on the cut name
    with the help of the cut factory implementation. '''
    cut_id = cut.cut_name
    if "." in cut.cut_name:
        cut_id = cut.cut_name.split(".")[0]
    common_cut = common_cuts_impl(cut_id)
    factory = cut_factory_switch(common_cut)
    cut_fact = CutFactory(factory, cut, sci_alert, obs_window)
    return cut_fact.cut_value


class common_cuts_impl(Enum):
    ''' available common cuts which are used to setup the cut correctly
     via the cut factory. '''
    from_parameter = "alert_parameter"
    max_delay = 'max_delay'
    min_delay = 'min_delay'
    currently_in_schedule = 'currently_in_schedule'
    position_changed = 'position_changed'
    position_uncertainty = 'position_uncertainty'


def cut_factory_switch(factory):
    ''' cut factory '''
    switcher = {common_cuts_impl.from_parameter: cut_from_alert_parameter,
                common_cuts_impl.max_delay: cut_max_delay,
                common_cuts_impl.min_delay: cut_min_delay,
                common_cuts_impl.currently_in_schedule: cut_currently_in_schedule,
                common_cuts_impl.position_changed: cut_position_changed,
                common_cuts_impl.position_uncertainty: cut_position_uncertainty}
    func = switcher.get(factory)
    return func()


class cut_from_alert_parameter:
    ''' apply a cut derived from a voevent parameter '''
    def determine_parameter(self, cut, sci_alert, obs_window):
        param = cut.cut_name.split(".")[1]
        param_search = ".//Param[@name='%s']" % param
        param_val = sci_alert.alert.find(param_search).attrib['value']
        print(param, "---->", param_val, type(param_val))
        return param_val


class cut_max_delay:
    ''' cuts on the delay of a potentially found observation window. '''
    def determine_parameter(self, cut, sci_alert, obs_window):
        # print(obs_window.delay, type(obs_window.delay))
        return obs_window.delay


class cut_min_delay:
    ''' cut on the delay of a potentially found observation window. '''
    def determine_parameter(self, cut, sci_alert, obs_window):
        return obs_window.delay


class cut_currently_in_schedule:
    ''' cut to determine if this alert is already being observed. '''
    def determine_parameter(self, cut, sci_alert, obs_winodw):
        # TODO: needs access to current observations
        return True


class cut_position_changed:
    ''' cut to determine if the position has changed with respect to the
        previous alert of the same astrophysical event. '''
    def determine_parameter(self, cut, sci_alert, obs_window):
        pos_change = 0 * u.deg
        try:
            prev_alert = sci_alert.alert.Citations.EventIVORN
            if prev_alert:
                pos_change = 5 * u.deg
                # TODO: query the associated previous alert and compute the position delta
            else:
                return pos_change
        except Exception as x:
            print(x)

        return pos_change


class cut_position_uncertainty:
    ''' cut to determine by how much the position uncertainty has changed '''
    def determine_parameter(self, cut, sci_alert, obs_window):
        coords = vp.get_event_position(sci_alert)
        pos_uncert = coords.err * coords.units
        return pos_uncert


class CutFactory:
    ''' factory class for all cuts. '''
    def __init__(self, factory, cut, sci_alert, obs_window):
        self.factory = factory
        self.cut_value = self.factory.determine_parameter(cut, sci_alert, obs_window)


def str2bool(in_val):
    is_true = in_val.lower() in ("yes", "true")
    is_false = in_val.lower() in ("no", "false")
    # print(v, "        -", "is_true=", is_true, "is_false=", is_false)
    if is_true:
        return True
    if is_false:
        return False
    else:
        return None


def parse_value(in_val):
    # print("parsing:", in_val, type(in_val))
    out_val = None

    if isinstance(in_val, Quantity):
        out_val = in_val
        return out_val

    if isinstance(in_val, float):
        out_val = in_val
        return out_val

    if isinstance(in_val, int):
        out_val = float(in_val)

    if isinstance(in_val, bool):
        out_val = in_val
        return out_val

    if isinstance(in_val, str):
        if str2bool(in_val) is not None:
            out_val = str2bool(in_val)
            return out_val
        else:
            try:
                out_val = float(in_val)
                return out_val
            except ValueError:
                pass
            try:
                out_val = Quantity(in_val)
                return out_val
            except TypeError:
                out_val = in_val
                return out_val

    return out_val


class cut:
    ''' base class for cuts, holding the name, required value, comparison, type of cut and actual value '''
    def __init__(self, name, required_value, comp, cut_type, custom_origin=None, actual_value=None):
        # print(" *** ", name, "***")
        self.cut_name = name

        self.required_value = None
        self.actual_value = None

        self.required_value = parse_value(required_value)
        # print("parsed required:", self.required_value, type(self.required_value))
        if actual_value is not None:
            self.actual_value = parse_value(actual_value)
            # print("parsed actual:", self.actual_value, type(self.actual_value))

        self.comparator = Comparator(comp)
        self.custom_origin = custom_origin
        self.cut_type = cut_type

        self.performed = False
        self.passed = False
        # self.evalulate()

    def evaluate(self):
        ''' actual evaluation of a cut '''
        # print(self.cut_name, self.required_value, self.comparator, self.actual_value)
        # print(self.required_value, self.comparator, self.actual_value)
        self.convert_values_to_float()
        # check common data type
        if not isinstance(self.required_value, type(self.actual_value)):
            if inf in [self.required_value, self.actual_value]:
                self.passed = False
                self.performed = True
                return
            print("Wrong data type! Can't Evaluate. Cut Failed!")  # Error
            self.passed = False
            return

        # check comparable units
        if isinstance(self.required_value, Quantity) and isinstance(self.actual_value, Quantity):
            if not self.required_value.unit.si.bases == self.actual_value.unit.si.bases:
                print("Units have uncommon bases. Cut Failed!")  # Error!
                self.passed = False
                return

        is_equal = False
        is_less = False
        is_greater = False

        is_equal = self.required_value == self.actual_value
        is_less = self.required_value >= self.actual_value
        is_greater = self.required_value <= self.actual_value

        if self.comparator is Comparator.equal:
            self.passed = is_equal
        if self.comparator is Comparator.greater:
            self.passed = is_greater
        if self.comparator is Comparator.less:
            self.passed = is_less

        self.performed = True

    def convert_values_to_float(self):
        if isinstance(self.required_value, int):
            self.required_value = float(self.required_value)
        if isinstance(self.actual_value, int):
            self.actual_value = float(self.actual_value)
        try:
            self.actual_value = float(self.actual_value)
        except Exception:
            pass

    def __str__(self):
        out = ""
        name = self.cut_name
        if self.custom_origin:
            name = self.custom_origin + "." + self.cut_name
        if self.actual_value and not self.performed:
            out = "   *  \'{}\' {} {}  -> actual value: {}".format(name, self.comparator.value,
                                                                   self.required_value,
                                                                   self.actual_value)
        else:
            out += "  *  \'{}\' {} {}  -> actual value: {}".format(name,
                                                                   self.comparator.value,
                                                                   self.required_value,
                                                                   self.actual_value)
            if self.passed:
                out += "  -> cut passed."
            else:
                out += "  -> cut failed."

        return out


def voevent_type_parse(value, comp):
    if value is "true":
        return True
    if value is "false":
        return False

    if comp is Comparator.equal:
        return str(value)

    return float(value)

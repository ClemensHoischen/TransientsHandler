'''
Contains all the classes needed for scheduling blocks
'''
import scheduling_block_factory as sbf


class TH_SchedulingBlock:
    def __init__(self):
        self.sched_block_id = None
        self.proposal = SbProposal()
        self.configuration = SbConfiguration()
        self.ObservationBlocks = []

    def BuildBlock(self, input):
        block_factory = sbf.sb_factory()
        pass


class TH_ObservationBlock:
    def __init__(self):
        self.observation_block_id = None
        self.source = ObSource()
        self.observation_conditions = None
        self.script_id = None
        self.max_script_duration = None


class SbProposal:
    def __init__(self):
        self.proposal_id = None
        self.proposal_type = None
        self.proposal_priority = None


class SbConfiguration:
    def __init__(self):
        self.instrument = None
        self.camera_cfg = None
        self.rta_cfg = None


class ObSource:
    def __init__(self):
        self.source_id = None
        self.priposal_type = None
        self.proposal_priority = None
        self.region_of_interest = None
        self.observing_mode = None
        self.coordinates = None


class ObObservationConditions:
    def __init__(self):
        self.start_time = None
        self.duration = None
        self.tolerance = None
        self.quality = ObQuality()
        self.weather = ObWeahter()


class ObQuality:
    def __init__(self):
        self.min_nsb_range = None
        self.max_nsb_range = None
        self.illumination = None


class ObWeahter:
    def __init__(self):
        self.precision_pointing = None
        self.wind_speed = None
        self.humidity = None
        self.cloudiness = None

'''
container module for different types of observation types supported by the TH
'''


class Wobble:
    ''' wobble observation type - direct copy forom the SB defintion'''
    def __init__(self, offset, angle):
        self.type = "wobble"
        self.offset = offset
        self.angle = angle

    def __str__(self):
        return "%s : offset = %s, angle = %s" % (self.type, self.offset, self.angle)


class RasterScan:
    ''' raser scan observation type.
    only as excample that multple types need to be supported for now. '''
    def __init__(self):
        self.type = 'raster_scan'
        self.x_scan = None
        self.y_scan = None
        self.grid_spacing = None

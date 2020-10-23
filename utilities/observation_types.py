class wobble:
    def __init__(self):
        self.type = "wobble"
        self.offset = None
        self.angle = None

    def __str__(self):
        return "%s : offset = %s, angle = %s" % (self.type, self.offset, self.angle)


class raster_scan:
    def __init__(self):
        self.type = 'raster_scan'
        self.x_scan = None
        self.y_scan = None
        self.grid_spacing = None

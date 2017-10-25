class Zone:
    def __init__(self, label, x, y, z):
        self.label = label
        self.x = x
        self.y = y
        self.z = z

    def show(self):
        print("# Zone : %s" % (self.label))
        print("#     Coordinates : (%s,%s,%s)" % (self.x, self.y, self.z))

    def to_string(self):
        return "%3s %3s %3s %3s" % (self.label,
                                    self.x,
                                    self.y,
                                    self.z)

    def __repr__(self):
        return "%s" % (self.label)

    def __hash__(self):
        return hash(self.label)

    def __str__(self):
        return "%s" % (self.label)

    def __eq__(self, other):
        return self.label == other.label


def SearchZone(list, label):
    for zone in list:
        if zone.label == label:
            return zone
    return None

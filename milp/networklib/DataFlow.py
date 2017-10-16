class DataFlow:
    def __init__(self, id, label, source, target, size, max_delay, max_error):
        self.id = id
        self.label = label
        self.source = source
        self.target = target
        self.size = size
        self.max_delay = max_delay
        self.max_error = max_error
        self.allowed = []
        self.deployedIn = {None, int}

    def hasTask(self, task):
        if (self.source == task):
            return True
        elif (self.target == task):
            return True
        else:
            return False

    def concernsZones(self, zone1, zone2):
        if (self.source.zone == zone1 and self.target.zone == zone2):
            return True
        elif (self.source.zone == zone2 and self.target.zone == zone1):
            return True
        else:
            return False

    def setAllowedChannel(self, channel):
        self.allowed.append(channel)

    def getAllowedChannel(self):
        return self.allowed

    def setDeployedIn(self, channel, channelIndex):
        self.deployedIn = [channel, channelIndex]

    def getDeployedIn(self):
        return self.deployedIn

    def show(self):
        print("# DataFlow : %s" % (self.label))
        print("#     Source    : %s" % (self.source))
        print("#     Target    : %s" % (self.target))
        print("#     Size      : %s" % (self.size))
        print("#     Max Delay : %s" % (self.max_delay))
        print("#     Max Error : %s" % (self.max_error))

    def to_string(self):
        return "%3s %-15s %-15s %-15s %5s %5s %5s" % (self.id,
                                                      self.label,
                                                      self.source,
                                                      self.target,
                                                      self.size,
                                                      self.max_delay,
                                                      self.max_error)

    def __repr__(self):
        return "%s" % (self.label)

    def __hash__(self):
        return hash(self.label)

    def __str__(self):
        return "%s" % (self.label)

    def __eq__(self, other):
        return self.label == other.label

    def __cmp__(self, other):
        if hasattr(other, 'id'):
            return self.id.__cmp__(other.id)
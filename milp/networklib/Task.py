class Task:
    def __init__(self, id, label, size, zone, mobile):
        self.id = id
        self.label = label
        self.size = size
        self.zone = zone
        self.mobile = mobile
        self.allowed = []
        self.deployedIn = {None, int, None}

    def setAllowedNode(self, node):
        self.allowed.append(node)

    def getAllowedNode(self):
        return self.allowed

    def setDeployedIn(self, node, nodeIndex, zone):
        self.deployedIn = [node, nodeIndex, zone]

    def getDeployedIn(self):
        return self.deployedIn

    def show(self):
        print("# Task : %s" % (self.label))
        print("#     Size   : %s" % (self.size))
        print("#     Zone   : %s" % (self.zone))
        print("#     Mobile : %s" % (self.mobile))

    def to_string(self):
        return "%3s %-15s %5s %5s %1s" % (self.id,
                                          self.label,
                                          self.size,
                                          self.zone,
                                          self.mobile)

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


def SearchTask(list, label):
    for task in list:
        if task.label == label:
            return task
    return None

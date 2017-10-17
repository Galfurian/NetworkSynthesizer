class Node:
    def __init__(self, label, id, cost, size, energy, task_energy, mobile):
        self.label = label
        self.id = id
        self.cost = cost
        self.size = size
        self.energy = energy
        self.task_energy = task_energy
        self.mobile = mobile
        self.allowed = []

    def setAllowedTask(self, task):
        self.allowed.append(task)

    def getAllowedTask(self):
        return self.allowed

    def show(self):
        print("# Node : %s" % (self.label))
        print("#     Id          : %s" % (self.id))
        print("#     Cost        : %s" % (self.cost))
        print("#     Size        : %s" % (self.size))
        print("#     Energy      : %s" % (self.energy))
        print("#     Task Energy : %s" % (self.task_energy))
        print("#     Mobile      : %s" % (self.mobile))

    @staticmethod
    def get_header():
        return "%-15s | %2s | %5s | %10s | %6s | %12s | %6s |" % ("label",
                                                                "id",
                                                                "cost",
                                                                "size",
                                                                "energy",
                                                                "task_energy",
                                                                "mobile")

    @staticmethod
    def get_header_caps():
        return "%-15s | %2s | %5s | %10s | %6s | %12s | %6s |" % ("LABEL",
                                                                "ID",
                                                                "COST",
                                                                "SIZE",
                                                                "ENERGY",
                                                                "TASK ENERGY",
                                                                "MOBILE")

    def to_string(self):
        return "%-15s | %2s | %5s | %10s | %6s | %12s | %6s |" % (self.label,
                                                                self.id,
                                                                self.cost,
                                                                self.size,
                                                                self.energy,
                                                                self.task_energy,
                                                                self.mobile)

    def __repr__(self):
        return "%s" % (self.label)

    def __hash__(self):
        return hash(self.label)

    def __str__(self):
        return "%s" % (self.label)

    def __cmp__(self, other):
        if hasattr(other, 'id'):
            return self.id.__cmp__(other.id)

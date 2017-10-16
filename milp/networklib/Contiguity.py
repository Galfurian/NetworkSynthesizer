class Contiguity:
    def __init__(self, zone_one, zone_two, channel, conductance, deploymentCost):
        self.zone_one = zone_one
        self.zone_two = zone_two
        self.channel = channel
        self.conductance = conductance
        self.deploymentCost = deploymentCost

    def show(self):
        print("# Contiguity : %s" % ("Contiguity_%s_%s_%s" % (self.zone_one, self.zone_two, self.channel)))
        print("#     Zone1       :%s" % (self.zone_one))
        print("#     Zone2       :%s" % (self.zone_two))
        print("#     Channel     :%s" % (self.channel))
        print("#     Conductance :%s" % (self.conductance))
        print("#     Deployment  :%s" % (self.deploymentCost))

    def to_string(self):
        return "%3s %3s %-15s %-5s %8s" % (self.zone_one,
                                           self.zone_two,
                                           self.channel,
                                           self.conductance,
                                           self.deploymentCost)

    def __repr__(self):
        return "%s" % (self.conductance)

    def __hash__(self):
        return hash("Contiguity_%s_%s_%s" % (self.zone_one, self.zone_two, self.channel))

    def __str__(self):
        return "%s" % (self.conductance)
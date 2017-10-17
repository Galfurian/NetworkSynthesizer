class Channel:
    def __init__(self, label, id, cost, size, energy, df_energy, delay, error, wireless, max_conn):
        self.label = label
        self.id = id
        self.cost = cost
        self.size = size
        self.energy = energy
        self.df_energy = df_energy
        self.delay = delay
        self.error = error
        self.wireless = wireless
        self.max_conn = max_conn
        self.allowed = []
        self.allowedBetween = {}

    def setAllowedDataFlow(self, dataflow):
        self.allowed.append(dataflow)

    def getAllowedDataFlow(self):
        return self.allowed

    def setAllowedBetween(self, zone1, zone2):
        self.allowedBetween[zone1, zone2] = True

    def isAllowedBetween(self, zone1, zone2):
        return self.allowedBetween.get((zone1, zone2), False)

    def show(self):
        print("# Channel : %s" % (self.label))
        print("#     Id        : %s" % (self.id))
        print("#     Cost      : %s" % (self.cost))
        print("#     Size      : %s" % (self.size))
        print("#     Energy    : %s" % (self.energy))
        print("#     DF Energy : %s" % (self.df_energy))
        print("#     Delay     : %s" % (self.delay))
        print("#     Error     : %s" % (self.error))
        print("#     Wireless  : %s" % (self.wireless))
        print("#     Max Conn  : %s" % (self.max_conn))

    @staticmethod
    def get_header():
        return "%-15s | %2s | %5s | %10s | %6s | %10s | %6s | %6s | %8s | %8s |" % ("label",
                                                                                    "id",
                                                                                    "cost",
                                                                                    "size",
                                                                                    "energy",
                                                                                    "df_energy",
                                                                                    "delay",
                                                                                    "error",
                                                                                    "wireless",
                                                                                    "max_conn")

    @staticmethod
    def get_header_caps():
        return "%-15s | %2s | %5s | %10s | %6s | %10s | %6s | %6s | %8s | %8s |" % ("LABEL",
                                                                                    "ID",
                                                                                    "COST",
                                                                                    "SIZE",
                                                                                    "ENERGY",
                                                                                    "DF_ENERGY",
                                                                                    "DELAY",
                                                                                    "ERROR",
                                                                                    "WIRELESS",
                                                                                    "MAX_CONN")

    def to_string(self):
        return "%-15s | %2s | %5s | %10s | %6s | %10s | %6s | %6s | %8s | %8s |" % (self.label,
                                                                                    self.id,
                                                                                    self.cost,
                                                                                    self.size,
                                                                                    self.energy,
                                                                                    self.df_energy,
                                                                                    self.delay,
                                                                                    self.error,
                                                                                    self.wireless,
                                                                                    self.max_conn)

    def toScnsl(self):
        ChannelSetupName = ("csb_%s" % (self.id))
        ChToScnsl = ("Scnsl::BuiltinPlugin::CoreChannelSetup_t %s;\n" % (ChannelSetupName))
        ChToScnsl += ("%s.name         = \"%s\";\n" % (ChannelSetupName, self.label))
        ChToScnsl += ("%s.extensionId  = \"core\";\n" % (ChannelSetupName))
        ChToScnsl += ("%s.capacity     = %s;\n" % (ChannelSetupName, self.size))
        ChToScnsl += ("%s.delay        = sc_core::sc_time(%s, sc_core::SC_MS);\n" % (ChannelSetupName, self.delay))
        if (self.wireless):
            ChToScnsl += ("%s.channel_type = Scnsl::BuiltinPlugin::CoreChannelSetup_t::SHARED;\n" % (ChannelSetupName))
            ChToScnsl += ("%s.nodes_number = 0;" % (ChannelSetupName))
            ChToScnsl += (
                "%s.propagation  = Scnsl::BuiltinPlugin::CoreChannelSetup_t::EM_SPEED;\n" % (ChannelSetupName))
        else:
            ChToScnsl += (
                "%s.channel_type = Scnsl::BuiltinPlugin::CoreChannelSetup_t::FULL_DUPLEX;\n" % (ChannelSetupName))
            ChToScnsl += ("%s.capacity2    = %s;\n" % (ChannelSetupName, self.size))
        return ChToScnsl

    def __repr__(self):
        return "%s" % (self.label)

    def __hash__(self):
        return hash(self.label)

    def __str__(self):
        return "%s" % (self.label)

    def __cmp__(self, other):
        if hasattr(other, 'id'):
            return self.id.__cmp__(other.id)


def SearchChannel(list, id):
    for channel in list:
        if channel.id == id:
            return channel
    return None

import sys

import itertools

from Node import *
from Channel import *
from Zone import *
from Contiguity import *
from Task import *
from DataFlow import *


def RoundInt(x):
    if x == float("inf"):
        return +sys.maxint
    if x == float("-inf"):
        return -sys.maxint
    return int(round(x))


class NetworkInstance:
    def __init__(self):
        self.channels = []
        self.nodes = []
        self.zones = []
        self.contiguities = {}
        self.tasks = []
        self.dataflows = []

    def add_channel(self, channel):
        self.channels.append(channel)

    def add_node(self, node):
        self.nodes.append(node)

    def add_zone(self, zone):
        self.zones.append(zone)

    def add_contiguity(self, contiguity):
        self.contiguities.append(contiguity)

    def add_taks(self, taks):
        self.tasks.append(taks)

    def add_data_flow(self, data_flow):
        self.dataflows.append(data_flow)

    def load_node_catalog(self, node_file):
        print("* %s" % Node.get_header_caps())
        with open(node_file, "r") as nodeFile:
            for line in nodeFile:
                if (line[0] != ';') and (line[0] != '#'):
                    nodeLine = line.strip()
                    # Retrieve the values from the file.
                    try:
                        ndLabel, ndId, ndCost, ndSize, ndEnergy, ndTaskEnergy, ndMobile = nodeLine.split()
                    except ValueError:
                        print("Error: Wrong line format '%s'" % nodeLine)
                        exit(1)
                    # Create a new node.
                    NewNode = Node(ndLabel,
                                   int(ndId),
                                   int(ndCost),
                                   int(ndSize),
                                   int(ndEnergy),
                                   int(ndTaskEnergy),
                                   int(ndMobile))
                    # Append the node to the list of nodes.
                    self.add_node(NewNode)
                    # Print the node.
                    print("* %s" % NewNode.to_string())
                    # Delete the auxiliary variables.
                    del nodeLine, NewNode, ndLabel, ndId, ndCost, ndSize, ndMobile, ndEnergy, ndTaskEnergy

    def load_channel_catalog(self, channel_file):
        print("* %s" % Channel.get_header_caps())
        with open(channel_file, "r") as channelFile:
            for line in channelFile:
                if (line[0] != ';') and (line[0] != '#'):
                    channelLine = line.strip()
                    # Retrieve the values from the file.
                    try:
                        chLabel, chId, chCost, chSize, chEnergy, chDfEnergy, chDelay, chError, chWireless, ch_max_conn = channelLine.split()
                    except ValueError:
                        print("Error: Wrong line format '%s'" % channelLine)
                        exit(1)
                    # Create a new Channel.
                    NewChannel = Channel(chLabel,
                                         int(chId),
                                         int(chCost),
                                         int(chSize),
                                         int(chEnergy),
                                         int(chDfEnergy),
                                         int(chDelay),
                                         int(chError),
                                         int(chWireless),
                                         RoundInt(float(ch_max_conn)))
                    # Append the channel to the list of channels.
                    self.add_channel(NewChannel)
                    # Print the channel.
                    print("* %s" % NewChannel.to_string())
                    # Delete the auxiliary variables.
                    del channelLine, NewChannel, chLabel, chId, chCost, chSize, chEnergy, chDfEnergy, chDelay, chError, chWireless

    def load_input_instance(self, input_file):
        ParsingZone = False
        ParsingContiguity = False
        ParsingTask = False
        ParsingDataflow = False
        TaskIndex = 1
        DataFlowIndex = 1

        with open(input_file, "r") as inputFile:
            for line in inputFile:
                inputLine = line.strip()
                # Skip empty lines.
                if not inputLine:
                    continue
                # Skip comments.
                if (inputLine[0] == ';') or (inputLine[0] == '#'):
                    continue
                # Parse the line.
                if inputLine == "<ZONE>":
                    ParsingZone = True
                    print("* LOADING ZONES")
                elif inputLine == "</ZONE>":
                    ParsingZone = False
                    print("* LOADING ZONES - Done")
                elif ParsingZone:
                    # Retrieve the values from the file.
                    try:
                        zn_label, zn_x, zn_y, zn_z = inputLine.split()
                    except ValueError:
                        print("Error: Wrong line format '%s'" % inputLine)
                        exit(1)
                    # Create a new zone.
                    NewZone = Zone(int(zn_label),
                                   int(zn_x),
                                   int(zn_y),
                                   int(zn_z))
                    # Append the zone to the list of zones.
                    self.add_zone(NewZone)
                    # Print the zone.
                    print("* %s" % NewZone.to_string())
                    # Delete the auxiliary variables.
                    del NewZone, zn_label, zn_x, zn_y, zn_z

                elif inputLine == "<CONTIGUITY>":
                    ParsingContiguity = True
                    print("* LOADING CONTIGUITIES")
                elif inputLine == "</CONTIGUITY>":
                    ParsingContiguity = False
                    print("* LOADING CONTIGUITIES - Done")
                elif ParsingContiguity:
                    # Retrieve the values from the file.
                    try:
                        cnt_zone1, cnt_zone2, cnt_channel, cnt_conductance, cnt_deployment_cost = inputLine.split()
                    except ValueError:
                        print("Error: Wrong line format '%s'" % inputLine)
                        exit(1)
                    # Search the instance of the first zone.
                    SearchedZone1 = SearchZone(self.zones, int(cnt_zone1))
                    if SearchedZone1 is None:
                        print("[Error] Can't find zone : %s" % cnt_zone1)
                        exit(1)
                    # Search the instance of the first zone.
                    SearchedZone2 = SearchZone(self.zones, int(cnt_zone2))
                    if SearchedZone2 is None:
                        print("[Error] Can't find zone : %s" % cnt_zone2)
                        exit(1)
                    # Search the instance of the channel.
                    SearchedChannel = SearchChannel(self.channels, int(cnt_channel))
                    if SearchedChannel is None:
                        print("[Error] Can't find channel : %s" % cnt_channel)
                        exit(1)
                    # Create the new contiguity.
                    NewContiguity = Contiguity(SearchedZone1,
                                               SearchedZone2,
                                               SearchedChannel,
                                               float(cnt_conductance),
                                               float(cnt_deployment_cost))
                    # Add the contiguity to the list of contiguities.
                    self.contiguities[SearchedZone1, SearchedZone2, SearchedChannel] = NewContiguity
                    # Set the same values for the vice-versa of the zones.
                    self.contiguities[SearchedZone2, SearchedZone1, SearchedChannel] = NewContiguity
                    # Print the contiguity.
                    print("* %s" % NewContiguity.to_string())
                    # Delete the auxiliary variables.
                    del inputLine, NewContiguity, SearchedZone1, SearchedZone2, SearchedChannel
                    del cnt_zone1, cnt_zone2, cnt_channel, cnt_conductance, cnt_deployment_cost

                elif inputLine == "<TASK>":
                    ParsingTask = True
                    print("* LOADING TASKS")
                elif inputLine == "</TASK>":
                    ParsingTask = False
                    print("* LOADING TASKS - Done")
                elif ParsingTask:
                    # Retrieve the values from the file.
                    try:
                        tsk_label, tsk_size, tsk_zone, tsk_mobile = inputLine.split()
                    except ValueError:
                        print("Error: Wrong line format '%s'" % inputLine)
                        exit(1)
                    # Search the instance of the zone.
                    SearchedZone = SearchZone(self.zones, int(tsk_zone))
                    if SearchedZone is None:
                        print("[Error] Can't find zone : %s" % tsk_zone)
                        exit(1)
                    # Create the new task.
                    NewTask = Task(TaskIndex, tsk_label, int(tsk_size), SearchedZone, int(tsk_mobile))
                    # Append the task to the list of tasks.
                    self.add_taks(NewTask)
                    # Increment the task index
                    TaskIndex += 1
                    # Print the task.
                    print("* %s" % NewTask.to_string())
                    # Clear the variables.
                    del inputLine, tsk_label, tsk_size, tsk_zone, tsk_mobile, NewTask

                elif inputLine == "<DATAFLOW>":
                    ParsingDataflow = True
                    print("* LOADING DATA-FLOWS")
                elif inputLine == "</DATAFLOW>":
                    ParsingDataflow = False
                    print("* LOADING DATA-FLOWS - Done")
                elif ParsingDataflow:
                    # Retrieve the values from the file.
                    try:
                        df_label, df_source, df_target, df_band, df_delay, df_error = inputLine.split()
                    except ValueError:
                        print("Error: Wrong line format '%s'" % inputLine)
                        exit(1)
                    # Search the instance of the source task.
                    SourceTask = SearchTask(self.tasks, df_source)
                    if SourceTask is None:
                        print("[Error] Can't find the source task : %s" % df_source)
                        exit(1)
                    # Search the instance of the target task.
                    TargetTask = SearchTask(self.tasks, df_target)
                    if TargetTask is None:
                        print("[Error] Can't find the target task : %s" % df_target)
                        exit(1)
                    # Check if the source and target task are the same.
                    if SourceTask == TargetTask:
                        print(
                            "[Error] Can't define a dataflow between the same task : %s -> %s" % (
                                SourceTask, TargetTask))
                        exit(1)
                    # Create the new Data-Flow
                    NewDataFlow = DataFlow(DataFlowIndex,
                                           df_label,
                                           SourceTask,
                                           TargetTask,
                                           int(df_band),
                                           int(df_delay),
                                           int(df_error))
                    # Append the data-flow to the list of data-flows.
                    self.add_data_flow(NewDataFlow)
                    # Print the data-flow.
                    print("* %s" % NewDataFlow.to_string())
                    # Increment the index of data-flows.
                    DataFlowIndex += 1
                    # Clear the variables.
                    del df_label, df_source, df_target, df_band, df_delay, df_error
                    del SourceTask, TargetTask, NewDataFlow

        # Clean auxiliary variables.
        del ParsingZone
        del ParsingContiguity
        del ParsingTask
        del ParsingDataflow
        del TaskIndex
        del DataFlowIndex

    # By default set the unknown contiguities to 0.0, unless the pair is composed by the same zone, in that case its 1.0.
    def define_missing_contiguities(self):
        for zone1 in self.zones:
            for zone2 in self.zones:
                for channel in self.channels:
                    if self.contiguities.get((zone1, zone2, channel)) is None:
                        if zone1 == zone2:
                            self.contiguities[zone1, zone2, channel] = Contiguity(zone1, zone2, channel, 1.0, 0)
                            print("* %s" % self.contiguities[zone1, zone2, channel].to_string())
                        else:
                            self.contiguities[zone1, zone2, channel] = Contiguity(zone1, zone2, channel, 0.0,
                                                                                  sys.maxint)
                    del channel
                del zone2
            del zone1

    def perform_preprocess(self):
        print("* Checking in which nodes the tasks can be placed into...")
        for task, node in itertools.product(self.tasks, self.nodes):
            # Check if the task and the node are compatible.
            if task.mobile != node.mobile:
                continue
            # Check if the task can be contained inside the node.
            if task.size > node.size:
                continue
            # Link node and task.
            task.setAllowedNode(node)
            node.setAllowedTask(task)

        print("* Checking in which channels the data-flows can be placed into...")
        for dataflow, channel in itertools.product(self.dataflows, self.channels):
            contiguity = self.contiguities.get((dataflow.source.zone, dataflow.target.zone, channel))
            # Check the conductance of the contiguity.
            if contiguity.conductance <= 0:
                continue
            # Check if the channel can hold the data-flow give the conductance value.
            if channel.size < (dataflow.size / contiguity.conductance):
                continue
            # Check if the channel has the required error_rate demanded by the data-flow give the conductance value.
            if channel.error > (dataflow.max_error * contiguity.conductance):
                continue
            # Check if the channel has the required delay demanded by the data-flow give the conductance value.
            if channel.delay > (dataflow.max_delay * contiguity.conductance):
                continue
            # If a node is mobile, then it can be connected only to wireless channels.
            if ((dataflow.source.mobile or dataflow.target.mobile) and not channel.wireless):
                continue
            # Link dataflow and channel.
            dataflow.setAllowedChannel(channel)
            channel.setAllowedDataFlow(dataflow)
            # Delete the contiguity.
            del contiguity

    def perform_precheck(self):
        print("* Checking if there is at least one suitable node for each task...")
        for task in self.tasks:
            if len(task.getAllowedNode()) == 0:
                print("There are no nodes that can contain task %s." % task)
                exit(1)

        print("* Checking if there are suitable channels for data-flows which cross zones...")
        for dataflow in self.dataflows:
            if len(dataflow.getAllowedChannel()) == 0:
                # Get the source and target node
                source_node = dataflow.source
                target_node = dataflow.target
                # If the tasks resides in different zones, then there is no way the dataflow can be correctly placed.
                if source_node.zone != target_node.zone:
                    print("There are no channels that can contain data-flow %s." % dataflow)
                    for channel in self.channels:
                        reason = "no reason"
                        contiguity = self.contiguities.get((source_node.zone, target_node.zone, channel))
                        if contiguity.conductance <= 0:
                            reason = "low conductance %s" % contiguity.conductance
                        elif channel.size < (dataflow.size / contiguity.conductance):
                            reason = "low size"
                        elif channel.error > (dataflow.max_error * contiguity.conductance):
                            reason = "higher error rate"
                        elif channel.delay > (dataflow.max_delay * contiguity.conductance):
                            reason = "higher delay"
                        elif ((source_node.mobile or target_node.mobile) and not channel.wireless):
                            reason = "unacceptable mobile/wireless"
                        print("\tChannel %s for %s." % (channel, reason))
                    exit(1)
                # If they resides in the same zone, there is a chance that the two tasks can be placed inside the same,
                # node. However, this must be checked.
                SumSizes = source_node.size + target_node.size
                CanBeContained = False
                for node in set(source_node.getAllowedNode()).intersection(target_node.getAllowedNode()):
                    if node.size >= SumSizes:
                        CanBeContained = True
                        break

                if not CanBeContained:
                    print("There are no channels that can contain data-flow %s." % dataflow)
                    print("And also there is no node which can contain both of its tasks.")

                del source_node
                del target_node
                del SumSizes
                del CanBeContained

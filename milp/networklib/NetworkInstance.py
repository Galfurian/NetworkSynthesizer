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
        self.sol_N = 0
        self.sol_C = 0
        self.sol_x = 0
        self.sol_y = 0
        self.sol_w = 0
        self.sol_h = 0

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

    def load_node_catalog(self, node_catalog_filename):
        print("* %s" % Node.get_header_caps())
        with open(node_catalog_filename, "r") as node_file:
            for line in node_file:
                node_line = line.strip()
                # Skip empty lines.
                if not node_line:
                    continue
                # Skip comments.
                if (node_line[0] == ';') or (node_line[0] == '#'):
                    continue
                # Retrieve the values from the file.
                try:
                    label, id, cost, size, energy, task_energy, energy_cost, mobile = node_line.split()
                except ValueError:
                    print("Error: Wrong line format '%s'" % node_line)
                    return False
                # Create a new node.
                new_node = Node(label,
                                int(id),
                                int(cost),
                                int(size),
                                int(energy),
                                int(task_energy),
                                float(energy_cost),
                                int(mobile))
                # Append the node to the list of nodes.
                self.add_node(new_node)
                # Print the node.
                print("* %s" % new_node.to_string())
                # Delete the auxiliary variables.
                del node_line, new_node
                del label, id, cost, size, energy, task_energy, mobile
        return True

    def load_channel_catalog(self, channel_catalog_filename):
        print("* %s" % Channel.get_header_caps())
        with open(channel_catalog_filename, "r") as channel_file:
            for line in channel_file:
                channel_line = line.strip()
                # Skip empty lines.
                if not channel_line:
                    continue
                # Skip comments.
                if (channel_line[0] == ';') or (channel_line[0] == '#'):
                    continue
                # Retrieve the values from the file.
                try:
                    label, id, cost, size, energy, df_energy, energy_cost, delay, error, wireless, point_to_point = channel_line.split()
                except ValueError:
                    print("Error: Wrong line format '%s'" % channel_line)
                    return False
                # Create a new Channel.
                new_channel = Channel(label,
                                      int(id),
                                      int(cost),
                                      int(size),
                                      int(energy),
                                      int(df_energy),
                                      float(energy_cost),
                                      int(delay),
                                      int(error),
                                      int(wireless),
                                      int(point_to_point))
                # Append the channel to the list of channels.
                self.add_channel(new_channel)
                # Print the channel.
                print("* %s" % new_channel.to_string())
                # Delete the auxiliary variables.
                del channel_line, new_channel
                del label, id, cost, size, energy, df_energy, delay, error, wireless, point_to_point
        return True

    def load_input_instance(self, input_instance_filename):
        is_parsing_zone = False
        is_parsing_contiguity = False
        is_parsing_task = False
        is_parsing_dataflow = False
        index_task = 1
        index_dataflow = 1

        with open(input_instance_filename, "r") as input_file:
            for line in input_file:
                input_line = line.strip()
                # Skip empty lines.
                if not input_line:
                    continue
                # Skip comments.
                if (input_line[0] == ';') or (input_line[0] == '#'):
                    continue

                # -----------------------------------------------------------------------------------------------------
                # Parse the line.
                if input_line == "<ZONE>":
                    is_parsing_zone = True
                    print("* LOADING ZONES")
                elif input_line == "</ZONE>":
                    is_parsing_zone = False
                    print("* LOADING ZONES - Done")
                elif is_parsing_zone:
                    # Retrieve the values from the file.
                    try:
                        label, x, y, z = input_line.split()
                    except ValueError:
                        print("Error: Wrong line format '%s'" % input_line)
                        return False
                    # Create a new zone.
                    new_zone = Zone(int(label), int(x), int(y), int(z))
                    # Append the zone to the list of zones.
                    self.add_zone(new_zone)
                    # Print the zone.
                    print("* %s" % new_zone.to_string())
                    # Delete the auxiliary variables.
                    del label, x, y, z
                    del new_zone

                # -----------------------------------------------------------------------------------------------------
                elif input_line == "<CONTIGUITY>":
                    is_parsing_contiguity = True
                    print("* LOADING CONTIGUITIES")
                elif input_line == "</CONTIGUITY>":
                    is_parsing_contiguity = False
                    print("* LOADING CONTIGUITIES - Done")
                elif is_parsing_contiguity:
                    # Retrieve the values from the file.
                    try:
                        id_zone1, id_zone2, id_channel, conductance, deployment_cost = input_line.split()
                    except ValueError:
                        print("Error: Wrong line format '%s'" % input_line)
                        return False
                    # Search the instance of the first zone.
                    zone1 = SearchZone(self.zones, int(id_zone1))
                    if zone1 is None:
                        print("[Error] Can't find zone : %s" % id_zone1)
                        return False
                    # Search the instance of the first zone.
                    zone2 = SearchZone(self.zones, int(id_zone2))
                    if zone2 is None:
                        print("[Error] Can't find zone : %s" % id_zone2)
                        return False
                    # Search the instance of the channel.
                    channel = SearchChannel(self.channels, int(id_channel))
                    if channel is None:
                        print("[Error] Can't find channel : %s" % id_channel)
                        return False
                    # Create the new contiguity.
                    new_contiguity = Contiguity(zone1,
                                                zone2,
                                                channel,
                                                float(conductance),
                                                float(deployment_cost))
                    # Add the contiguity to the list of contiguities.
                    self.contiguities[zone1, zone2, channel] = new_contiguity
                    # Set the same values for the vice-versa of the zones.
                    self.contiguities[zone2, zone1, channel] = new_contiguity
                    # Print the contiguity.
                    print("* %s" % new_contiguity.to_string())
                    # Delete the auxiliary variables.
                    del id_zone1, id_zone2, id_channel, conductance, deployment_cost
                    del zone1, zone2, channel
                    del new_contiguity

                # -----------------------------------------------------------------------------------------------------
                elif input_line == "<TASK>":
                    is_parsing_task = True
                    print("* LOADING TASKS")
                elif input_line == "</TASK>":
                    is_parsing_task = False
                    print("* LOADING TASKS - Done")
                elif is_parsing_task:
                    # Retrieve the values from the file.
                    try:
                        label, size, id_zone, mobile = input_line.split()
                    except ValueError:
                        print("Error: Wrong line format '%s'" % input_line)
                        return False
                    # Search the instance of the zone.
                    zone = SearchZone(self.zones, int(id_zone))
                    if zone is None:
                        print("[Error] Can't find zone : %s" % id_zone)
                        return False
                    # Create the new task.
                    new_task = Task(index_task, label, int(size), zone, int(mobile))
                    # Append the task to the list of tasks.
                    self.add_taks(new_task)
                    # Increment the task index
                    index_task += 1
                    # Print the task.
                    print("* %s" % new_task.to_string())
                    # Clear the variables.
                    del label, size, id_zone, mobile
                    del zone
                    del new_task

                # -----------------------------------------------------------------------------------------------------
                elif input_line == "<DATAFLOW>":
                    is_parsing_dataflow = True
                    print("* LOADING DATA-FLOWS")
                elif input_line == "</DATAFLOW>":
                    is_parsing_dataflow = False
                    print("* LOADING DATA-FLOWS - Done")
                elif is_parsing_dataflow:
                    # Retrieve the values from the file.
                    try:
                        label, id_source, id_target, band, delay, error = input_line.split()
                    except ValueError:
                        print("Error: Wrong line format '%s'" % input_line)
                        return False
                    # Search the instance of the source task.
                    source = SearchTask(self.tasks, id_source)
                    if source is None:
                        print("[Error] Can't find the source task : %s" % id_source)
                        return False
                    # Search the instance of the target task.
                    TargetTask = SearchTask(self.tasks, id_target)
                    if TargetTask is None:
                        print("[Error] Can't find the target task : %s" % id_target)
                        return False
                    # Check if the source and target task are the same.
                    if source == TargetTask:
                        print("[Error] Can't define a dataflow between the same task : %s -> %s"
                              % (source, TargetTask))
                        return False
                    # Create the new Data-Flow
                    NewDataFlow = DataFlow(index_dataflow,
                                           label,
                                           source,
                                           TargetTask,
                                           int(band),
                                           int(delay),
                                           int(error))
                    # Append the data-flow to the list of data-flows.
                    self.add_data_flow(NewDataFlow)
                    # Print the data-flow.
                    print("* %s" % NewDataFlow.to_string())
                    # Increment the index of data-flows.
                    index_dataflow += 1
                    # Clear the variables.
                    del label, id_source, id_target, band, delay, error
                    del source, TargetTask
                    del NewDataFlow

                # Clear the variables.
                del input_line
                del line

        # Clean auxiliary variables.
        del is_parsing_zone
        del is_parsing_contiguity
        del is_parsing_task
        del is_parsing_dataflow
        del index_task
        del index_dataflow
        return True

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
                return False

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
                    return False
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
                    return False

                del source_node
                del target_node
                del SumSizes
                del CanBeContained
        return True

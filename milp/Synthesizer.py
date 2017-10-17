#!/usr/bin/python
# File    : Synthesizer.py
# Created : 5 Mar 2015, last revision: 10 May 2016.
# Authors : Enrico Fraccaroli, Romeo Rizzi
# Content : A MILP model for the mobile network design problem proposed by Davide Quaglia et al.
# We refer to the LaTex/pdf document for a description of the model.

import os
import time
from sys import argv, exit

from gurobipy import *

from networklib.Channel import *
from networklib.Contiguity import *
from networklib.DataFlow import *
from networklib.Node import *
from networklib.Task import *
from networklib.Zone import *
from networklib.NetworkChecker import *
from networklib.ScnslGenerator import *
from networklib.TechLibPrinter import *
from networklib.UmlForScilabPrinter import *
from networklib.NetworkInstance import *


def Separator():
    print("*******************************************************************************")


def Usage():
    About()
    Separator()
    print("* Usage:")
    print("*     %s [Arguments]" % os.path.basename(argv[0]))
    print("*")
    print("* Arguments:")
    print("*     [1] : Input Instance.")
    print("*     [2] : Nodes Catalogue.")
    print("*     [3] : Channels Catalogue.")
    print("*     [4] : Optimization Objective: {1:Cost (Def), 2:Energy, 3:Delay, 4:Error}")
    print("*     [5] : Generate XML:           {0:No   (Def), 1:Yes}")
    print("*     [6] : Generate SCNSL:         {0:No   (Def), 1:Yes}")
    Separator()
    exit(1)


def About():
    Separator()
    print("* Network Synthesizer")
    print("* Version : 0.1")
    print("* Authors : Enrico Fraccaroli, Romeo Rizzi")
    Separator()


# ---------------------------------------------------------------------------------------------------------------------
# Files parsing starting time.
parse_timer_begin = time.time()

OPTIMIZATION = 1
XML_GENERATION = 0
SCNSL_GENERATION = 0
VERBOSE = 1

# ---------------------------------------------------------------------------------------------------------------------
argc = len(argv)
if (argc <= 2) or (argc >= 7):
    Usage()

if argc >= 5:
    OPTIMIZATION = int(argv[4])
    if (OPTIMIZATION <= 0) or (OPTIMIZATION >= 6):
        Usage()

if argc >= 6:
    XML_GENERATION = int(argv[5])
    if (XML_GENERATION != 0) and (XML_GENERATION != 1):
        Usage()

if argc >= 7:
    SCNSL_GENERATION = int(argv[6])
    if (SCNSL_GENERATION != 0) and (SCNSL_GENERATION != 1):
        Usage()

# ---------------------------------------------------------------------------------------------------------------------
# Start with the general information.
About()

# The catalogs and input lists
NodeList = []
ChannelList = []
ZoneList = []
ContiguityList = {}
TaskList = []
DataFlowList = []

# ---------------------------------------------------------------------------------------------------------------------
Separator()
print("* READING NODEs CATALOG FILE")
Separator()
print("* %s" % Node.get_header_caps())
with open(argv[2], "r") as nodeFile:
    for line in nodeFile:
        if (line[0] != ';') and (line[0] != '#'):
            nodeLine = line.strip()
            # Retrieve the values from the file.
            try:
                ndLabel, ndId, ndCost, ndSize, ndEnergy, ndTaskEnergy, ndMobile = nodeLine.split()
            except ValueError:
                print("Error: Wrong line format '%s'" % nodeLine)
                continue
            # Create a new node.
            NewNode = Node(ndLabel, int(ndId), int(ndCost), int(ndSize), int(ndEnergy), int(ndTaskEnergy),
                           int(ndMobile))
            # Append the node to the list of nodes.
            NodeList.append(NewNode)
            # Print the node.
            print("* %s" % NewNode.to_string())
            # Delete the auxiliary variables.
            del nodeLine, NewNode, ndLabel, ndId, ndCost, ndSize, ndMobile, ndEnergy, ndTaskEnergy

# ---------------------------------------------------------------------------------------------------------------------
Separator()
print("* READING CHANNELSs CATALOG FILE")
Separator()
print("* %s" % Channel.get_header_caps())

with open(argv[3], "r") as channelFile:
    for line in channelFile:
        if (line[0] != ';') and (line[0] != '#'):
            channelLine = line.strip()
            # Retrieve the values from the file.
            try:
                chLabel, chId, chCost, chSize, chEnergy, chDfEnergy, chDelay, chError, chWireless, ch_max_conn = channelLine.split()
            except ValueError:
                print("Error: Wrong line format '%s'" % channelLine)
                continue
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
                                 float(ch_max_conn))
            # Append the channel to the list of channels.
            ChannelList.append(NewChannel)
            # Print the channel.
            print("* %s" % NewChannel.to_string())
            # Delete the auxiliary variables.
            del channelLine, NewChannel, chLabel, chId, chCost, chSize, chEnergy, chDfEnergy, chDelay, chError, chWireless

# ---------------------------------------------------------------------------------------------------------------------
Separator()
print("* READING INPUT INSTANCE FILE")
Separator()
ParsingZone = False
ParsingContiguity = False
ParsingTask = False
ParsingDataflow = False
TaskIndex = 1
DataFlowIndex = 1

with open(argv[1], "r") as inputFile:
    for line in inputFile:
        inputLine = line.strip()
        if (inputLine[0] != ';') and (inputLine[0] != '#'):
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
                    continue
                # Create a new zone.
                NewZone = Zone(int(zn_label),
                               int(zn_x),
                               int(zn_y),
                               int(zn_z))
                # Append the zone to the list of zones.
                ZoneList.append(NewZone)
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
                    continue
                # Search the instance of the first zone.
                SearchedZone1 = SearchZone(ZoneList, int(cnt_zone1))
                if SearchedZone1 is None:
                    print("[Error] Can't find zone : %s" % cnt_zone1)
                    exit(1)
                # Search the instance of the first zone.
                SearchedZone2 = SearchZone(ZoneList, int(cnt_zone2))
                if SearchedZone2 is None:
                    print("[Error] Can't find zone : %s" % cnt_zone2)
                    exit(1)
                # Search the instance of the channel.
                SearchedChannel = SearchChannel(ChannelList, int(cnt_channel))
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
                ContiguityList[SearchedZone1, SearchedZone2, SearchedChannel] = NewContiguity
                # Set the same values for the vice-versa of the zones.
                ContiguityList[SearchedZone2, SearchedZone1, SearchedChannel] = NewContiguity
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
                    continue
                # Search the instance of the zone.
                SearchedZone = SearchZone(ZoneList, int(tsk_zone))
                if SearchedZone is None:
                    print("[Error] Can't find zone : %s" % tsk_zone)
                    exit(1)
                # Create the new task.
                NewTask = Task(TaskIndex, tsk_label, int(tsk_size), SearchedZone, int(tsk_mobile))
                # Append the task to the list of tasks.
                TaskList.append(NewTask)
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
                    continue
                # Search the instance of the source task.
                SourceTask = SearchTask(TaskList, df_source)
                if SourceTask is None:
                    print("[Error] Can't find the source task : %s" % df_source)
                    exit(1)
                # Search the instance of the target task.
                TargetTask = SearchTask(TaskList, df_target)
                if TargetTask is None:
                    print("[Error] Can't find the target task : %s" % df_target)
                    exit(1)
                # Check if the source and target task are the same.
                if SourceTask == TargetTask:
                    print("[Error] Can't define a dataflow between the same task : %s -> %s" % (SourceTask, TargetTask))
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
                DataFlowList.append(NewDataFlow)
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
Separator()

# ---------------------------------------------------------------------------------------------------------------------
# ---------------------------------------------------------------------------------------------------------------------
# By default set the unknown contiguities to 0.0, unless the pair is composed by the same zone, in that case its 1.0.
print("* DEFINING MISSING CONTIGUITIES")
for zone1 in ZoneList:
    for zone2 in ZoneList:
        for channel in ChannelList:
            if ContiguityList.get((zone1, zone2, channel)) is None:
                if zone1 == zone2:
                    ContiguityList[zone1, zone2, channel] = Contiguity(zone1, zone2, channel, 1.0, 0)
                else:
                    ContiguityList[zone1, zone2, channel] = Contiguity(zone1, zone2, channel, 0.0, sys.maxint)
            del channel
        del zone2
    del zone1

# Print the contiguities.
for zone1 in ZoneList:
    for zone2 in ZoneList:
        for channel in ChannelList:
            contiguity = ContiguityList.get((zone1, zone2, channel))
            if contiguity.conductance > 0 and contiguity.zone_one != contiguity.zone_two:
                print("* %s" % contiguity.to_string())
            del channel, contiguity
        del zone2
    del zone1

# Files parsing ending time.
parse_timer_end = time.time()

Separator()

exit(0)
# ---------------------------------------------------------------------------------------------------------------------
# ---------------------------------------------------------------------------------------------------------------------
Separator()
print("* PRE-PROCESSING")
Separator()

# Datastructures starting time.
structure_timer_begin = time.time()
print("* Checking in which nodes the tasks can be placed into...")
for task in TaskList:
    for node in NodeList:
        if task.mobile <= node.mobile:
            if task.size <= node.size:
                task.setAllowedNode(node)
                node.setAllowedTask(task)

print("* Checking in which channels the data-flows can be placed into...")
for dataflow in DataFlowList:
    for channel in ChannelList:
        contiguity = ContiguityList.get((dataflow.source.zone, dataflow.target.zone, channel))
        # Check the conductance of the contiguity.
        if contiguity.conductance > 0:
            # Check if the channel can hold the data-flow give the conductance value.
            if channel.size >= (dataflow.size / contiguity.conductance):
                # Check if the channel has the required error_rate demanded by the data-flow give the conductance value.
                if channel.error <= (dataflow.max_error * contiguity.conductance):
                    # Check if the channel has the required delay demanded by the data-flow give the conductance value.
                    if channel.delay <= (dataflow.max_delay * contiguity.conductance):
                        dataflow.setAllowedChannel(channel)
                        channel.setAllowedDataFlow(dataflow)
        del contiguity

print("* Checking if there is a suitable node for each task...")
for task in TaskList:
    # print("*     Task '%15s' Nodes : %s" % (task, task.getAllowedNode()))
    if len(task.getAllowedNode()) == 0:
        print("There are no node which can contain task %s." % task)
        exit(1)

if VERBOSE:
    Separator()
    print("* The tasks can be placed into:")
    for task in TaskList:
        print("*     Task '%15s' Nodes : %s" % (task, task.getAllowedNode()))
    print("*")
    print("* The data-flows can be placed into:")
    for dataflow in DataFlowList:
        print("*     DataFlow '%15s' Channels : %s" % (dataflow, dataflow.getAllowedChannel()))

    print("*")
    print("* The nodes can host:")
    for node in NodeList:
        print("*     Node '%15s' Tasks : %s" % (node, node.getAllowedTask()))

    print("*")
    print("* The channels can host:")
    for channel in ChannelList:
        print("*     Channel '%15s' Data-Flows : %s" % (channel, channel.getAllowedDataFlow()))

Separator()

# ---------------------------------------------------------------------------------------------------------------------
# ---------------------------------------------------------------------------------------------------------------------
Separator()
print("* GENERATING OPTIMIZATION MODEL")
Separator()

# Create the model.
m = Model('DistributedEmbededSystem')

# ---------------------------------------------------------------------------------------------------------------------
# ---------------------------------------------------------------------------------------------------------------------
Separator()
print("* GENERATING VARIABLES")
Separator()

# Create the model variables.
UB_on_N = {}
UB_on_C = {}
N = {}
C = {}
x = {}
y = {}
md = {}
gamma = {}
rho = {}
w = {}
h = {}
j = {}
q = {}

# Create the support variables.
indexSetOfClonesOfNodesInArea = {}
indexSetOfClonesOfChannel = {}

# ---------------------------------------------------------------------------------------------------------------------
for zone in ZoneList:
    for node in NodeList:
        UB_on_N[node, zone] = len([task for task in node.getAllowedTask() if task.zone == zone])
        indexSetOfClonesOfNodesInArea[node, zone] = range(1, UB_on_N[node, zone] + 1)
print("*")
print("* UB_on_N [%s]" % len(UB_on_N))
print("* \tVariable UB_on_N is the upper-bound on the number of nodes of a certain")
print("* \ttype inside a given zone. This value can be pre-computed.")
print("*")

# ---------------------------------------------------------------------------------------------------------------------
for channel in ChannelList:
    UB_on_C[channel] = len(channel.getAllowedDataFlow())
    indexSetOfClonesOfChannel[channel] = range(1, UB_on_C[channel] + 1)
print("*")
print("* UB_on_C [%s]" % len(UB_on_C))
print("* \tVariable UB_on_C is the upper-bound on the number of channels of a certain")
print("* \ttype. This upper-bound can be pre-computed")
print("*")

# ---------------------------------------------------------------------------------------------------------------------
for node in NodeList:
    for zone in ZoneList:
        N[node, zone] = m.addVar(lb=0.0,
                                 ub=UB_on_N[node, zone],
                                 obj=0.0,
                                 vtype=GRB.CONTINUOUS,
                                 name='N_%s_%s' % (node, zone))
# Log the information concerning the variable.
print("*")
print("* N [%s]" % len(N))
print("* \tVariable N identifies the number of deployed nodes of a certain type inside")
print("* \ta given zone. The upper-bound on this variable is equal to UB_on_N.")
print("*")

# ---------------------------------------------------------------------------------------------------------------------
for channel in ChannelList:
    C[channel] = m.addVar(lb=0.0,
                          ub=UB_on_C[channel],
                          obj=0.0,
                          vtype=GRB.CONTINUOUS,
                          name='C_%s' % channel)
# Log the information concerning the variable.
print("*")
print("* C [%s]" % len(C))
print("* \tVariable C identifies the number of deployed channels of a certain type.")
print("* \tThe upper-bound on this variable is equal to UB_on_C.")
print("*")

# ---------------------------------------------------------------------------------------------------------------------
for node in NodeList:
    for zone in ZoneList:
        for nodeIndex in indexSetOfClonesOfNodesInArea[node, zone]:
            x[node, nodeIndex, zone] = m.addVar(lb=0.0,
                                                ub=1.0,
                                                obj=0.0,
                                                vtype=GRB.BINARY,
                                                name='x_%s_%s_%s' % (node, nodeIndex, zone))
# Log the information concerning the variable.
print("*")
print("* x [%s]" % len(x))
print("* \tVariable x identifies the number of nodes of a given type deployed inside")
print("* \ta given zone. If the variable x[n1,n1q,z1] is true, it means that")
print("* \tthere are n1q nodes of type n1 inside zone z1.")
print("*")

# ---------------------------------------------------------------------------------------------------------------------
for channel in ChannelList:
    for channelIndex in indexSetOfClonesOfChannel[channel]:
        y[channel, channelIndex] = m.addVar(lb=0.0,
                                            ub=1.0,
                                            obj=0.0,
                                            vtype=GRB.BINARY,
                                            name='y_%s_%s' % (channel, channelIndex))
# Log the information concerning the variable.
print("*")
print("* y [%s]" % len(y))
print("* \tVariable y identifies the number of deployed channels for a given type of")
print("* \tchannel. In particular, if the variable y[c1,c1q] is true, it means that")
print("* \tthere are c1q channels of type c1 deployed inside the network.")
print("*")

# ---------------------------------------------------------------------------------------------------------------------
for dataflow in DataFlowList:
    md[dataflow] = m.addVar(lb=0.0,
                            ub=1.0,
                            obj=0.0,
                            vtype=GRB.BINARY,
                            name='md_%s' % dataflow)
# Log the information concerning the variable.
print("*")
print("* md [%s]" % len(md))
print("* \tVariable md identifies if at least one of the tasks connected by a given")
print("* \tdata-flow is a mobile task.")
print("*")

# ---------------------------------------------------------------------------------------------------------------------
for dataflow in DataFlowList:
    for task in TaskList:
        if dataflow.hasTask(task) is False:
            gamma[dataflow, task] = m.addVar(lb=0.0,
                                             ub=1.0,
                                             obj=0.0,
                                             vtype=GRB.BINARY,
                                             name='gamma_%s_%s' % (dataflow, task))
        else:
            gamma[dataflow, task] = m.addVar(lb=1.0,
                                             ub=1.0,
                                             obj=0.0,
                                             vtype=GRB.BINARY,
                                             name='gamma_%s_%s' % (dataflow, task))
# Log the information concerning the variable.
print("*")
print("* gamma [%s]" % len(gamma))
print("* \tVariable gamma identifies if the given task is not the source or target")
print("* \ttask of the given data-flow.")
print("*")

# ---------------------------------------------------------------------------------------------------------------------
for task1 in TaskList:
    for task2 in TaskList:
        if task1 != task2:
            rho[task1, task2] = m.addVar(lb=0.0,
                                         ub=1.0,
                                         obj=0.0,
                                         vtype=GRB.BINARY,
                                         name='rho_%s_%s' % (task1, task2))
# Log the information concerning the variable.
print("*")
print("* rho [%s]" % len(rho))
print("* \tVariable rho identifies if two tasks are deployed inside two different")
print("* \tnodes.")
print("*")

# ---------------------------------------------------------------------------------------------------------------------
for task in TaskList:
    for node in task.getAllowedNode():
        for nodeIndex in indexSetOfClonesOfNodesInArea[node, task.zone]:
            w[task, node, nodeIndex] = m.addVar(lb=0.0,
                                                ub=1.0,
                                                obj=0.0,
                                                vtype=GRB.BINARY,
                                                name='w_%s_%s_%s' % (task, node, nodeIndex))
# Log the information concerning the variable.
print("*")
print("* w [%s]" % len(w))
print("* \tVariable w identifies if the given task has been deployed inside the ")
print("* \tgiven instance of the given type of node.")
print("*")

# ---------------------------------------------------------------------------------------------------------------------
for dataflow in DataFlowList:
    for channel in dataflow.getAllowedChannel():
        for channelIndex in indexSetOfClonesOfChannel[channel]:
            h[dataflow, channel, channelIndex] = m.addVar(lb=0.0,
                                                          ub=1.0,
                                                          obj=0.0,
                                                          vtype=GRB.BINARY,
                                                          name='h_%s_%s_%s' % (dataflow, channel, channelIndex))
# Log the information concerning the variable.
print("*")
print("* h [%s]" % len(h))
print("* \tVariable h identifies if the given data-flow has been deployed inside the ")
print("* \tgiven instance of the given type of channel.")
print("*")

# ---------------------------------------------------------------------------------------------------------------------
for zone1 in ZoneList:
    for zone2 in ZoneList:
        for channel in ChannelList:
            if ContiguityList.get((zone1, zone2, channel)).conductance > 0:
                q[channel, zone1, zone2] = True
            else:
                q[channel, zone1, zone2] = False
print("*")
print("* q [%s]" % len(q))
print("* \tVariable q is pre-computed and identifies if the given type of channel")
print("* \tcan be placed between the given pair of zones.")
print("*")

# ---------------------------------------------------------------------------------------------------------------------
for zone1 in ZoneList:
    for zone2 in ZoneList:
        for channel in ChannelList:
            if ContiguityList.get((zone1, zone2, channel)).conductance > 0:
                for channelIndex in indexSetOfClonesOfChannel[channel]:
                    channel.setAllowedBetween(zone1, zone2)
                    j[channel, channelIndex, zone1, zone2] = m.addVar(lb=0.0,
                                                                      ub=1.0,
                                                                      obj=0.0,
                                                                      vtype=GRB.BINARY,
                                                                      name='j_%s_%s_%s_%s' % (
                                                                          channel, channelIndex, zone1, zone2))
            else:
                for channelIndex in indexSetOfClonesOfChannel[channel]:
                    j[channel, channelIndex, zone1, zone2] = m.addVar(lb=0.0,
                                                                      ub=0.0,
                                                                      obj=0.0,
                                                                      vtype=GRB.BINARY,
                                                                      name='j_%s_%s_%s_%s' % (
                                                                          channel, channelIndex, zone1, zone2))
# Log the information concerning the variable.
print("*")
print("* j [%s]" % len(j))
print("* \tVariable j identifies if the given instnace of the given channel has a ")
print("* \tvalid conductance between the given pari of zones.")
print("*")

# ---------------------------------------------------------------------------------------------------------------------
# Datastructures ending time.
structure_timer_end = time.time()

# Model update (force the take in of all the variables):
m.update()

# ---------------------------------------------------------------------------------------------------------------------
# ---------------------------------------------------------------------------------------------------------------------
# Constraints definition start.
constraints_timer_begin = time.time()

print("*******************************************************************************")
print("* Defining constraints...")
################################################################################
print("* Defining constraint C1")
# \forall n \in \Natu_{N}
for node in NodeList:
    # \forall z \in \Natu_{Z}
    for zone in ZoneList:
        # C1: N_{n,z} = \sum\limits_{p=1}^{\overline{N}_{n,z}} x_{n,z,p}
        m.addConstr(lhs=N[node, zone],
                    sense=GRB.EQUAL,
                    rhs=quicksum(x[node, nodeIndex, zone]
                                 for nodeIndex in indexSetOfClonesOfNodesInArea[node, zone]),
                    name="Define_N_%s_%s" % (node, zone))
################################################################################
print("* Defining constraint C2")
# \forall n \in \Natu_{N}
for node in NodeList:
    # \forall z \in \Natu_{Z}
    for zone in ZoneList:
        # \forall p \leq \overline{N}_{n,z}
        for nodeIndex in indexSetOfClonesOfNodesInArea[node, zone]:
            # C2: N_{n,z} \geq p * x_{n,z,p}
            m.addConstr(lhs=N[node, zone],
                        sense=GRB.GREATER_EQUAL,
                        rhs=nodeIndex * x[node, nodeIndex, zone],
                        name="Mono_clones_of_N_%s_%s_%s" % (node, zone, nodeIndex))

################################################################################
print("* Defining constraint C3")
# \forall c \in \Natu_{C}
for channel in ChannelList:
    # C3: C_{c} = \sum\limits_{p=1}^{\overline{C}_{c}} y_{c,p}
    m.addConstr(lhs=C[channel],
                sense=GRB.EQUAL,
                rhs=quicksum(y[channel, channelIndex]
                             for channelIndex in indexSetOfClonesOfChannel[channel]),
                name="Define_C_%s" % channel)
################################################################################
print("* Defining constraint C4")
# \forall c \in \Natu_{C}
for channel in ChannelList:
    # \forall p \leq \overline{C}_{c}
    for channelIndex in indexSetOfClonesOfChannel[channel]:
        # C4: C_{c} \geq p * y_{c,p}
        m.addConstr(lhs=C[channel],
                    sense=GRB.GREATER_EQUAL,
                    rhs=channelIndex * y[channel, channelIndex],
                    name="Mono_clones_of_C_%s_%s" % (channel, channelIndex))

###############################################################################
print("* Defining constraint C5")
# \forall t \in \Natu_{T}
for task in TaskList:
    # \forall n \in \alpha_{n}(t)
    for node in task.getAllowedNode():
        # \forall p \leq \overline{N}_{n,t.z}
        for nodeIndex in indexSetOfClonesOfNodesInArea[node, task.zone]:
            # C5: w_{t,n,p} \leq x_{n,t.z,p}
            m.addConstr(lhs=w[task, node, nodeIndex],
                        sense=GRB.LESS_EQUAL,
                        rhs=x[node, nodeIndex, task.zone],
                        name="Codomain_existance_for_w_%s_%s_%s" % (task, node, nodeIndex))

###############################################################################
print("* Defining constraint C6")
# \forall d \in \Natu_{D}
for dataflow in DataFlowList:
    # \forall c \in \alpha_{c}(d)
    for channel in dataflow.getAllowedChannel():
        # \forall p \leq \overline{C}_{c}
        for channelIndex in indexSetOfClonesOfChannel[channel]:
            # C6: h_{d,c,p} \leq y_{c,p}
            m.addConstr(lhs=h[dataflow, channel, channelIndex],
                        sense=GRB.LESS_EQUAL,
                        rhs=y[channel, channelIndex],
                        name="Codomain_existance_for_h_%s_%s_%s" % (dataflow, channel, channelIndex))

###############################################################################
print("* Defining constraint C7")
# \forall n \in \Natu_{N}
for node in NodeList:
    # \forall z \in \Natu_{Z}
    for zone in ZoneList:
        # \forall p \leq \overline{N}_{n,z}
        for nodeIndex in indexSetOfClonesOfNodesInArea[node, zone]:
            # C7: x_{n,z,p} \leq \sum\limits_{t}^{(\alpha_{t}(n) \wedge t.z = z)} w_{t,n,p}
            m.addConstr(lhs=x[node, nodeIndex, zone],
                        sense=GRB.LESS_EQUAL,
                        rhs=quicksum(w[task, node, nodeIndex]
                                     for task in node.getAllowedTask()
                                     if task.zone == zone),
                        name="Deactivate_unecessary_clones_of_x_%s_%s_%s" % (node, zone, nodeIndex))

###############################################################################
print("* Defining constraint C8")
# \forall c \in \Natu_{C}
for channel in ChannelList:
    # \forall p \leq \overline{C}_{c}
    for channelIndex in indexSetOfClonesOfChannel[channel]:
        # C8: y_{c,p} \leq \sum\limits_{d}^{\alpha_{d}(c)} h_{d,c,p}
        m.addConstr(lhs=y[channel, channelIndex],
                    sense=GRB.LESS_EQUAL,
                    rhs=quicksum(h[dataflow, channel, channelIndex]
                                 for dataflow in channel.getAllowedDataFlow()),
                    name="Deactivate_unecessary_clones_of_y_%s_%s" % (channel, channelIndex))

###############################################################################
print("* Defining constraint C9")
# \forall n \in \Natu_{N}
for node in NodeList:
    # \forall z \in \Natu_{Z}
    for zone in ZoneList:
        # \forall p \leq \overline{N}_{n,z}
        for nodeIndex in indexSetOfClonesOfNodesInArea[node, zone]:
            # C9: \sum\limits_{t}^{(\alpha_{t}(n) \wedge t.z = z)} t.s * w_{t,n,p} \leq n.s
            m.addConstr(lhs=quicksum((task.size * w[task, node, nodeIndex])
                                     for task in node.getAllowedTask()
                                     if task.zone == zone),
                        sense=GRB.LESS_EQUAL,
                        rhs=node.size,
                        name="Node_size_%s_%s" % (node, nodeIndex))

###############################################################################
print("* Defining constraint C10")
# \forall c \in \Natu_{C}
for channel in ChannelList:
    # \forall p \leq \overline{C}_{c}
    for channelIndex in indexSetOfClonesOfChannel[channel]:
        # C10: \sum\limits_{d}^{\alpha_{d}(c)} \dfrac{d.s * h_{d,c,p}}{cont(d.ts.z, d.td.z, c).c} \leq c.s
        m.addConstr(lhs=quicksum(((dataflow.size * h[dataflow, channel, channelIndex]) /
                                  ContiguityList.get((dataflow.source.zone, dataflow.target.zone, channel)).conductance)
                                 for dataflow in channel.getAllowedDataFlow()),
                    sense=GRB.LESS_EQUAL,
                    rhs=channel.size,
                    name="Channel_size_%s_%s" % (channel, channelIndex))

###############################################################################
print("* Defining constraint C11")
# \forall t \in \Natu_{T}
for task in TaskList:
    # C11: \sum\limits_{n}^{\alpha_{n}(t)} \sum\limits_{p=1}^{\overline{N}_{n,t.z}} w_{t,n,p} = 1
    m.addConstr(lhs=quicksum(w[task, node, nodeIndex]
                             for node in task.getAllowedNode()
                             for nodeIndex in indexSetOfClonesOfNodesInArea[node, task.zone]),
                sense=GRB.EQUAL,
                rhs=1,
                name="Unique_mapping_of_task_%s" % task)

###############################################################################
print("* Defining constraint C12 and C13")
# \forall d \in \Natu_{D}
for dataflow in DataFlowList:
    if dataflow.source.zone != dataflow.target.zone:
        # d.ts.z \neq d.td.z
        # C12: \sum\limits_{c}^{\alpha_{c}(d)} \sum\limits_{p=1}^{\overline{C}_{c}} h_{d,c,p} = 1
        m.addConstr(lhs=quicksum(h[dataflow, channel, channelIndex]
                                 for channel in dataflow.getAllowedChannel()
                                 for channelIndex in indexSetOfClonesOfChannel[channel]),
                    sense=GRB.EQUAL,
                    rhs=1,
                    name="Unique_mapping_of_dataflow_%s" % dataflow)
    else:
        # d.ts.z = d.td.z
        # C13: \sum\limits_{c}^{\alpha_{c}(d)} \sum\limits_{p = 1}^{\overline{C}_{c}} h_{d,c,p} = \rho_{d.ts, d.td}
        m.addConstr(lhs=quicksum(h[dataflow, channel, channelIndex]
                                 for channel in dataflow.getAllowedChannel()
                                 for channelIndex in indexSetOfClonesOfChannel[channel]),
                    sense=GRB.EQUAL,
                    rhs=rho[dataflow.source, dataflow.target],
                    name="Unique_mapping_of_dataflow_%s" % dataflow)

###############################################################################
print("* Defining constraint C14 and C15")
# \forall d \in \Natu_{D}
for dataflow in DataFlowList:
    # (d.ts.m = true)
    if dataflow.source.mobile:
        # C14: \sum\limits_{n}^{\alpha_{n}(d.ts)} \sum\limits_{p = 1}^{\overline{N}_{n,d.ts.z}} w_{d.ts,v,p} \leq m_{d}
        m.addConstr(lhs=quicksum(w[dataflow.source, node, nodeIndex]
                                 for node in dataflow.source.getAllowedNode()
                                 if node.mobile
                                 for nodeIndex in indexSetOfClonesOfNodesInArea[node, dataflow.source.zone]),
                    sense=GRB.LESS_EQUAL,
                    rhs=md[dataflow],
                    name="Define_md_for_dataflow_%s" % dataflow)
    # (d.td.m = true)
    if dataflow.target.mobile:
        # C15: \sum\limits_{n}^{\alpha_{n}(d.td)} \sum\limits_{p = 1}^{\overline{N}_{n,d.td.z}} w_{d.td,v,p} \leq m_{d}
        m.addConstr(lhs=quicksum(w[dataflow.target, node, nodeIndex]
                                 for node in dataflow.target.getAllowedNode()
                                 if node.mobile
                                 for nodeIndex in indexSetOfClonesOfNodesInArea[node, dataflow.target.zone]),
                    sense=GRB.LESS_EQUAL,
                    rhs=md[dataflow],
                    name="Define_md_for_dataflow_%s" % dataflow)

###############################################################################
print("* Defining constraint C16 and C17")
# \forall d \in \Natu_{D}
for dataflow in DataFlowList:
    # d.ts.z \neq d.td.z
    if dataflow.source.zone != dataflow.target.zone:
        # C16: \sum\limits_{c}^{\alpha_{wc}(d)} \sum\limits_{p = 1}^{\overline{C}_{c}} h_{d,c,p} \leq m_{d}
        m.addConstr(lhs=md[dataflow],
                    sense=GRB.GREATER_EQUAL,
                    rhs=quicksum(h[dataflow, channel, channelIndex]
                                 for channel in dataflow.getAllowedChannel()
                                 if channel.wireless
                                 for channelIndex in indexSetOfClonesOfChannel[channel]),
                    name="Unique_mapping_of_dataflow_%s_wrt_wireless_channels" % dataflow)
    else:
        # d.ts.z = d.td.z
        # C17: \sum\limits_{c}^{\alpha_{wc}(d)}
        #      \sum\limits_{p = 1}^{\overline{C}_{c}} h_{d,c,p} \leq m_{d} + \rho_{d.ts, d.td} - 1
        m.addConstr(lhs=md[dataflow] + rho[dataflow.source, dataflow.target] - 1,
                    sense=GRB.GREATER_EQUAL,
                    rhs=quicksum(h[dataflow, channel, channelIndex]
                                 for channel in dataflow.getAllowedChannel()
                                 if channel.wireless
                                 for channelIndex in indexSetOfClonesOfChannel[channel]),
                    name="Unique_mapping_of_dataflow_%s_wrt_wireless_channels" % dataflow)

###############################################################################
print("* Defining constraint C18")
# \forall t \in \Natu_{T}
for task1 in TaskList:
    # \forall t' \in \Natu_{T}
    for task2 in TaskList:
        # t \neq t'
        if task1 != task2:
            # t.z = t'.z
            if task1.zone == task2.zone:
                # \forall n  \in \alpha_{n}(t)
                for node1 in task1.getAllowedNode():
                    # \forall n' \in \alpha_{n}(t')
                    for node2 in task2.getAllowedNode():
                        # \forall p  \in \overline{N}_{n,t.z}
                        for node1Index in indexSetOfClonesOfNodesInArea[node1, task1.zone]:
                            # \forall p' \in \overline{N}_{n',t'.z}
                            for node2Index in indexSetOfClonesOfNodesInArea[node2, task2.zone]:
                                # (n \neq n') \wedge (p \neq p')
                                if [node1, node1Index] != [node2, node2Index]:
                                    # C18: (w_{t, n, p} + w_{t', n', p'} - 1) \leq \rho_{t,t'}
                                    m.addConstr(lhs=rho[task1, task2],
                                                sense=GRB.GREATER_EQUAL,
                                                rhs=w[task1, node1, node1Index] + w[task2, node2, node2Index] - 1,
                                                name="Task_mapping_in_different_nodes_of_%s_%s" % (task1, task2))
            else:
                m.addConstr(lhs=rho[task1, task2],
                            sense=GRB.EQUAL,
                            rhs=1,
                            name='TwoTasks_%s_%s_IntoDifferentNodes' % (task1, task2))

###############################################################################
print("* Defining constraint C19")
# \forall c \in \Natu_{C}
for channel in ChannelList:
    # c.w = false
    if not channel.wireless:
        # \forall p \leq \overline{C}_{c}
        for channelIndex in indexSetOfClonesOfChannel[channel]:
            # \forall d \in \alpha_{d}(c)
            for dataflow1 in channel.getAllowedDataFlow():
                # \forall d' \in \alpha_{d}(c)
                for dataflow2 in channel.getAllowedDataFlow():
                    # d \neq d'
                    if dataflow1 < dataflow2:
                        # with d.ts \neq d.td \neq d'.ts
                        if len({dataflow1.source, dataflow1.target, dataflow2.source}) == 3:
                            # C19: (h_{d,c,p} + h_{d',c,p} + \gamma_{d,d'.ts}) &\leq 2
                            m.addConstr(lhs=h[dataflow1, channel, channelIndex] +
                                            h[dataflow2, channel, channelIndex] +
                                            gamma[dataflow1, dataflow2.source],
                                        sense=GRB.LESS_EQUAL,
                                        rhs=2,
                                        name="Cabled_channel_%s_%s_serves_only_two_nodes_SOURCE_CLASH%s_%s" % (
                                            channel, channelIndex, dataflow1, dataflow2))
                        # with d.ts \neq d.td \neq d'.td
                        if len({dataflow1.source, dataflow1.target, dataflow2.target}) == 3:
                            # C19: (h_{d,c,p} + h_{d',c,p} + \gamma_{d,d'.td}) &\leq 2
                            m.addConstr(lhs=h[dataflow1, channel, channelIndex] +
                                            h[dataflow2, channel, channelIndex] +
                                            gamma[dataflow1, dataflow2.target],
                                        sense=GRB.LESS_EQUAL,
                                        rhs=2,
                                        name='Cabled_channel_%s_%s_serves_only_two_nodes_TARGET_CLASH_%s_%s' % (
                                            channel, channelIndex, dataflow1, dataflow2))

###############################################################################
print("* Defining constraint C20")
# \forall d \in \Natu_{D}
for dataflow in DataFlowList:
    # \forall t \in \Natu_{T}
    for task in TaskList:
        # t \neq d.ts AND t \neq d.td
        if dataflow.hasTask(task) is False:
            if len({task.zone, dataflow.source.zone, dataflow.target.zone}) == 3:
                # with (d.ts.z \neq t.z) AND (d.td.z \neq t.z) AND (d.ts.z \neq d.ts.z)
                # C20: \gamma_{d, t} >= 1
                m.addConstr(lhs=gamma[dataflow, task],
                            sense=GRB.EQUAL,
                            rhs=1,
                            name="defGamma_%s_%s_%s" % (task, dataflow.source, dataflow.target))
            else:
                # with (d.ts.z \neq t.z) OR (d.td.z \neq t.z) OR (d.ts.z \neq d.ts.z)
                # C20: \gamma_{d, t} >= \rho_{t, d.ts} + \rho_{t, d.td} + \rho_{d.ts, d.td} - 2
                m.addConstr(lhs=gamma[dataflow, task],
                            sense=GRB.GREATER_EQUAL,
                            rhs=rho[task, dataflow.source] +
                                rho[task, dataflow.target] +
                                rho[dataflow.source, dataflow.target] - 2,
                            name="Define_gamma_variable_for_%s_%s_%s" % (
                                task, dataflow.source, dataflow.target))

###############################################################################
print("* Defining constraint C21")
# \forall z_1 \in \Natu_{Z}
for zone1 in ZoneList:
    # \forall z_2 \in \Natu_{Z}
    for zone2 in ZoneList:
        # \forall c \in \alpha_{cc}(z_1,z_2)
        for channel in ChannelList:
            if not channel.wireless:
                # \forall p \leq \overline{C}_{c}
                for channelIndex in indexSetOfClonesOfChannel[channel]:
                    # \forall d \in \alpha_{d}(c)
                    for dataflow in channel.getAllowedDataFlow():
                        # (d.ts.z = z_1) AND (d.td.z = z_2) OR (d.ts.z = z_2) AND (d.td.z = z_1)
                        if dataflow.concernsZones(zone1, zone2):
                            # C21: j_{c,p,z_1,z_2} >= h_{d,c,p}
                            m.addConstr(lhs=j[channel, channelIndex, zone1, zone2],
                                        sense=GRB.GREATER_EQUAL,
                                        rhs=h[dataflow, channel, channelIndex] * q[channel, zone1, zone2],
                                        name="Cabled_channel_%s_%s_between_zones_%s_%s" % (
                                            channel, channelIndex, zone1, zone2))
# rhs=h[dataflow, channel, channelIndex] * channel.isAllowedBetween(zone1, zone2),

###############################################################################
print("* Defining constraint C22")
# \forall c \in \Natu_{C}
for channel in ChannelList:
    # c.w = true
    if channel.wireless:
        # \forall p \leq \overline{C}_{c}
        for channelIndex in indexSetOfClonesOfChannel[channel]:
            # \forall d \in \alpha_{d}(c)
            for dataflow1 in channel.getAllowedDataFlow():
                # \forall d' \in \alpha_{d}(c)
                for dataflow2 in channel.getAllowedDataFlow():
                    # d \neq d'
                    if dataflow1 < dataflow2:
                        # C22: h_{d,c,p} + h_{d',c,p} <= 1 + q_{c, d.ts.z, d'.ts.z} *
                        #                                    q_{c, d.ts.z, d'.td.z} *
                        #                                    q_{c, d.td.z, d'.ts.z} *
                        #                                    q_{c, d.td.z, d'.ts.z}
                        m.addConstr(lhs=h[dataflow1, channel, channelIndex] + h[dataflow2, channel, channelIndex],
                                    sense=GRB.LESS_EQUAL,
                                    rhs=(1 +
                                         q[channel, dataflow1.source.zone, dataflow2.source.zone] *
                                         q[channel, dataflow1.source.zone, dataflow2.target.zone] *
                                         q[channel, dataflow1.target.zone, dataflow2.source.zone] *
                                         q[channel, dataflow1.target.zone, dataflow2.target.zone]),
                                    name="Wireless_with_df_%s_%s" % (dataflow1.label, dataflow2.label))

# END - The constraints section - END

# Constraints definition end.
constraints_timer_end = time.time()

print("*******************************************************************************")
print("* Defining the optimization objective:")

if OPTIMIZATION == 1:
    print("*    Economic Cost Minimization")
    # Economic Cost Minimization:
    #   Its objective is to minimize the global economic cost of the network.
    m.setObjective(
        quicksum(x[node, nodeIndex, zone] * node.cost
                 for node in NodeList
                 for zone in ZoneList
                 for nodeIndex in indexSetOfClonesOfNodesInArea[node, zone]) +
        quicksum(y[channel, channelIndex] * channel.cost
                 for channel in ChannelList
                 for channelIndex in indexSetOfClonesOfChannel[channel]) +
        quicksum(j[channel, channelIndex, zone1, zone2] * ContiguityList.get((zone1, zone2, channel)).deploymentCost
                 for zone1 in ZoneList
                 for zone2 in ZoneList
                 for channel in ChannelList
                 if not channel.wireless
                 if channel.isAllowedBetween(zone1, zone2)
                 for channelIndex in indexSetOfClonesOfChannel[channel]),
        GRB.MINIMIZE
    )
    m.update()
elif OPTIMIZATION == 2:
    print("*    Energy Consumption Minimization")
    # Energy Consumption Minimization:
    #   The second optimization objective is to minimize the global energy consumption of the network.
    m.setObjective(
        quicksum(x[node, nodeIndex, zone] * node.energy
                 for node in NodeList
                 for zone in ZoneList
                 for nodeIndex in indexSetOfClonesOfNodesInArea[node, zone]) +
        quicksum(w[task, node, nodeIndex] * node.task_energy * task.size
                 for task in TaskList
                 for node in task.getAllowedNode()
                 for nodeIndex in indexSetOfClonesOfNodesInArea[node, task.zone]) +
        quicksum(y[channel, channelIndex] * channel.energy
                 for channel in ChannelList
                 for channelIndex in indexSetOfClonesOfChannel[channel]) +
        quicksum(h[dataflow, channel, channelIndex] * channel.df_energy * dataflow.size /
                 ContiguityList.get((dataflow.source.zone, dataflow.target.zone, channel)).conductance
                 for dataflow in DataFlowList
                 for channel in dataflow.getAllowedChannel()
                 for channelIndex in indexSetOfClonesOfChannel[channel]),
        GRB.MINIMIZE
    )
    m.update()
elif OPTIMIZATION == 3:
    print("*    Transmission Delay Minimization")
    # Transmission Delay Minimization:
    #   The third possible constrains is on the overall delay of the network.
    #   Its purpose is to minimize the global transmission delay of the network.
    m.setObjective(
        quicksum(channel.delay * h[dataflow, channel, channelIndex] /
                 ContiguityList.get((dataflow.source.zone, dataflow.target.zone, channel)).conductance
                 for dataflow in DataFlowList
                 for channel in dataflow.getAllowedChannel()
                 for channelIndex in indexSetOfClonesOfChannel[channel]),
        GRB.MINIMIZE
    )
    m.update()
elif OPTIMIZATION == 4:
    print("*    Error Rate Minimization")
    # Error Rate Minimization:
    #   The optimization objective is to minimize the global error rate of the network.
    m.setObjective(
        quicksum(channel.error * h[dataflow, channel, channelIndex] /
                 ContiguityList.get((dataflow.source.zone, dataflow.target.zone, channel)).conductance
                 for dataflow in DataFlowList
                 for channel in dataflow.getAllowedChannel()
                 for channelIndex in indexSetOfClonesOfChannel[channel]),
        GRB.MINIMIZE
    )
    m.update()
elif OPTIMIZATION == 5:
    print("*    Error Rate and Delay Minimization")
    # Error Rate and Delay Minimization:
    #   The optimization objective is to minimize both the global error rate and delay of the network.
    m.setObjective(
        quicksum(
            (
                (channel.delay * h[dataflow, channel, channelIndex]) / (
                    ContiguityList.get((dataflow.source.zone, dataflow.target.zone, channel)).conductance) +
                (channel.error * h[dataflow, channel, channelIndex]) / (
                    ContiguityList.get((dataflow.source.zone, dataflow.target.zone, channel)).conductance)
            ) for dataflow in DataFlowList for channel in dataflow.getAllowedChannel() for channelIndex in
            indexSetOfClonesOfChannel[channel]
        ),
        GRB.MINIMIZE
    )
    m.update()

print("*******************************************************************************")
print("* Starting optimization...")

# Optimization start.
optimization_timer_begin = time.time()

# Compute optimal solution
m.optimize()

# Optimization end.
optimization_timer_end = time.time()

# print(solution
if m.status == GRB.status.OPTIMAL:
    print('Optimal objective: %g' % m.objVal)
    print("*******************************************************************************")
    print('# Optimal Solution')
    # Economic Cost
    TotalCostCable = 0
    TotalCostWirls = 0
    TotalCostNodes = 0
    # Energy Consumption
    TotalEnergyNodes = 0
    TotalEnergyNodesUsage = 0
    TotalEnergyChannel = 0
    TotalEnergyChannelUsage = 0
    # Communication Delay
    TotalDelayCable = 0
    TotalDelayWirls = 0
    # Error Rate
    TotalErrorRateCable = 0
    TotalErrorRateWirls = 0
    print('# List of activated nodes:')
    SolN = m.getAttr('x', N)
    for zone in ZoneList:
        for node in NodeList:
            if SolN[node, zone] > 0:
                TotalCostNodes += node.cost * SolN[node, zone]
                TotalEnergyNodes += node.energy * SolN[node, zone]
                print('    In zone %s, use %g nodes of type %s' % (zone, SolN[node, zone], node))

    print('# List of activated channels:')
    SolC = m.getAttr('x', C)
    for channel in ChannelList:
        if SolC[channel] > 0:
            if channel.wireless:
                TotalCostWirls += channel.cost * SolC[channel]
            else:
                TotalCostCable += channel.cost * SolC[channel]
            TotalEnergyChannel += channel.energy * SolC[channel]
            print('    Use %g channels of type %s' % (SolC[channel], channel))

    print('# Tasks allocation:')
    SolW = m.getAttr('x', w)
    for zone in ZoneList:
        for task in TaskList:
            if task.zone == zone:
                for node in task.getAllowedNode():
                    for nodeIndex in indexSetOfClonesOfNodesInArea[node, zone]:
                        if SolW[task, node, nodeIndex]:
                            TotalEnergyNodesUsage += (node.task_energy * task.size)
                            task.setDeployedIn(node, nodeIndex, zone)
                            print(
                                '    Task %s inside %s-th node of type %s within zone %s' % (
                                    task, nodeIndex, node, zone))

    print('# Data-Flows allocation:')
    SolH = m.getAttr('x', h)
    for dataflow in DataFlowList:
        for channel in dataflow.getAllowedChannel():
            contiguity = ContiguityList.get((dataflow.source.zone, dataflow.target.zone, channel))
            for channelIndex in indexSetOfClonesOfChannel[channel]:
                if SolH[dataflow, channel, channelIndex]:
                    dataflow.setDeployedIn(channel, channelIndex)
                    TotalEnergyChannelUsage += (channel.df_energy * dataflow.size)
                    if channel.wireless:
                        TotalDelayWirls += (channel.delay / contiguity.conductance)
                        TotalErrorRateWirls += (channel.error / contiguity.conductance)
                    else:
                        TotalDelayCable += (channel.delay / contiguity.conductance)
                        TotalErrorRateCable += (channel.error / contiguity.conductance)
                    print(
                        '    Dataflow %s inside %s-th channels of type %s' % (dataflow, channelIndex, channel))
            del contiguity

    SolY = m.getAttr('x', y)
    for channel in dataflow.getAllowedChannel():
        if not channel.wireless:
            for channelIndex in indexSetOfClonesOfChannel[channel]:
                if SolY[channel, channelIndex]:
                    deploymentCost = sys.maxint
                    for dataflow in channel.getAllowedDataFlow():
                        contiguity = ContiguityList.get((dataflow.source.zone, dataflow.target.zone, channel))
                        if SolH[dataflow, channel, channelIndex]:
                            deploymentCost = contiguity.deploymentCost
                        del contiguity
                    if channel.wireless:
                        TotalCostWirls += deploymentCost
                    else:
                        TotalCostCable += deploymentCost
                    del deploymentCost

    print("*")
    print("* Final Statistics:")
    print("*     Economic Cost      : %s" % (TotalCostNodes + TotalCostWirls + TotalCostCable))
    print("*         Nodes Deployment     : %s" % TotalCostNodes)
    print("*         Wireless Channels    : %s" % TotalCostWirls)
    print("*         Cable    Channels    : %s" % TotalCostCable)
    print("*     Energy Consumption : %s" % (
        TotalEnergyNodes + TotalEnergyNodesUsage + TotalEnergyChannel + TotalEnergyChannelUsage))
    print("*         Nodes Power          : %s" % TotalEnergyNodes)
    print("*         Nodes Power Usage    : %s" % TotalEnergyNodesUsage)
    print("*         Channels Power       : %s" % TotalEnergyChannel)
    print("*         Channels Power Usage : %s" % TotalEnergyChannelUsage)
    print("*     Total Delay        : %s" % (TotalDelayWirls + TotalDelayCable))
    print("*         Wireless Channels    : %s" % TotalDelayWirls)
    print("*         Cable    Channels    : %s" % TotalDelayCable)
    print("*     Total Error        : %s" % (TotalErrorRateWirls + TotalErrorRateCable))
    print("*         Wireless Channels    : %s" % TotalErrorRateWirls)
    print("*         Cable    Channels    : %s" % TotalErrorRateCable)

    checker = NetworkChecker(NodeList,
                             ChannelList,
                             ZoneList,
                             ContiguityList,
                             TaskList,
                             DataFlowList,
                             SolN,
                             SolC,
                             SolW,
                             SolH,
                             indexSetOfClonesOfChannel,
                             indexSetOfClonesOfNodesInArea)
    checker.checkNetwork()

elif m.status == GRB.Status.INF_OR_UNBD:
    print('Model is infeasible or unbounded')
    exit(0)
elif m.status == GRB.Status.INFEASIBLE:
    print('Model is infeasible')
    exit(0)
elif m.status == GRB.Status.UNBOUNDED:
    print('Model is unbounded')
    exit(0)
else:
    print('Optimization ended with status %d' % m.status)
    exit(0)

if XML_GENERATION == 1:
    print("*##########################################")
    print("* Generating UML for Scilab...")
    umlPrinter = UmlForScilabPrinter(NodeList,
                                     ChannelList,
                                     ZoneList,
                                     ContiguityList,
                                     TaskList,
                                     DataFlowList,
                                     SolN,
                                     SolC,
                                     SolW,
                                     SolH,
                                     indexSetOfClonesOfChannel,
                                     indexSetOfClonesOfNodesInArea)
    umlPrinter.printNetwork()
    print("*##########################################")
    print("* Generating Technological Library...")
    techLibPrinter = TechLibPrinter(NodeList, ChannelList)
    techLibPrinter.printTechLib()

if SCNSL_GENERATION == 1:
    scnslPrinter = ScnslGenerator(NodeList, ChannelList, ZoneList, ContiguityList, TaskList, DataFlowList, SolN,
                                  SolC,
                                  SolW, SolH, indexSetOfClonesOfChannel, indexSetOfClonesOfNodesInArea)
    scnslPrinter.printScnslNetwork("main.cc")

elapsed_parse = parse_timer_end - parse_timer_begin
elapsed_struc = structure_timer_end - structure_timer_begin
elapsed_const = constraints_timer_end - constraints_timer_begin
elapsed_optim = optimization_timer_end - optimization_timer_begin
elapsed_total = elapsed_parse + elapsed_struc + elapsed_const + elapsed_optim

# Print elapsed times.
print("*")
print("*##########################################")
print("* Statistics...")
print("*")
print("*    File parsing           : %s s" % elapsed_parse)
print("*    Structure creation     : %s s" % elapsed_struc)
print("*    Constraints definition : %s s" % elapsed_const)
print("*    Optimization           : %s s" % elapsed_optim)
print("*    Total : %s s" % elapsed_total)
print("*##########################################")

exit(0)

# Copyright 2016, Enrico Fraccaroli <enrico.fraccaroli@univr.com>
# License: The MIT License (http://www.opensource.org/licenses/mit-license.php)
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

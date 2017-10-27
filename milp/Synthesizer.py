#!/usr/bin/python
# File    : Synthesizer.py
# Created : 5 Mar 2015, last revision: 10 May 2016.
# Authors : Enrico Fraccaroli, Romeo Rizzi
# Content : A MILP model for the mobile network design problem proposed by Davide Quaglia et al.
# We refer to the LaTex/pdf document for a description of the model.

import time
from sys import argv, exit
import psutil

from gurobipy import *

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


def GetMemoryUsage():
    # return the memory usage in MB
    process = psutil.Process(os.getpid())
    mem = process.memory_info()[0] / float(2 ** 20)
    return mem


def RoundInt(x):
    if x == float("inf"):
        return +sys.maxint
    if x == float("-inf"):
        return -sys.maxint
    return int(round(x))


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

instance = NetworkInstance()

# ---------------------------------------------------------------------------------------------------------------------
Separator()
print("* READING NODEs CATALOG FILE")
Separator()
instance.load_node_catalog(argv[2])
Separator()

# ---------------------------------------------------------------------------------------------------------------------
Separator()
print("* READING CHANNELSs CATALOG FILE")
Separator()
instance.load_channel_catalog(argv[3])
Separator()

# ---------------------------------------------------------------------------------------------------------------------
Separator()
print("* READING INPUT INSTANCE FILE")
Separator()
instance.load_input_instance(argv[1])
Separator()

# ---------------------------------------------------------------------------------------------------------------------
Separator()
print("* DEFINING MISSING CONTIGUITIES")
Separator()
instance.define_missing_contiguities()
Separator()

# ---------------------------------------------------------------------------------------------------------------------
Separator()
print("* PERFORMING PRE-PROCESS PHASE")
Separator()
instance.perform_preprocess()
instance.perform_precheck()
Separator()

# ---------------------------------------------------------------------------------------------------------------------
if VERBOSE:
    Separator()
    print("* The tasks can be placed into:")
    for task in instance.tasks:
        print("*     Task '%15s' Nodes : %s" % (task, task.getAllowedNode()))
    print("*")
    print("* The data-flows can be placed into:")
    for dataflow in instance.dataflows:
        print("*     DataFlow '%15s' Channels : %s" % (dataflow, dataflow.getAllowedChannel()))

    print("*")
    print("* The nodes can host:")
    for node in instance.nodes:
        print("*     Node '%15s' Tasks : %s" % (node, node.getAllowedTask()))

    print("*")
    print("* The channels can host:")
    for channel in instance.channels:
        print("*     Channel '%15s' Data-Flows : %s" % (channel, channel.getAllowedDataFlow()))
    Separator()

# Files parsing ending time.
parse_timer_end = time.time()

# ---------------------------------------------------------------------------------------------------------------------
# ---------------------------------------------------------------------------------------------------------------------
# Make the timer start.
structure_timer_begin = time.time()

# ---------------------------------------------------------------------------------------------------------------------
Separator()
print("* GENERATING OPTIMIZATION MODEL")
Separator()

# Create the model.
m = Model('DistributedEmbededSystem')

# ---------------------------------------------------------------------------------------------------------------------
# VARIABLE GENERATION
# ---------------------------------------------------------------------------------------------------------------------
Separator()
print("* GENERATING VARIABLES")
Separator()

# Create the model variables.
UB_on_N = {}
Set_UB_on_N = {}
UB_on_C = {}
Set_UB_on_C = {}
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
# sigma = {}

# ---------------------------------------------------------------------------------------------------------------------
for zone in instance.zones:
    for node in instance.nodes:
        UB_on_N[node, zone] = len([task for task in node.getAllowedTask() if task.zone == zone])
        Set_UB_on_N[node, zone] = range(1, UB_on_N[node, zone] + 1)
# Log the information concerning the variable.
print("*")
print("* UB_on_N [%s]" % len(UB_on_N))
print("* \tVariable UB_on_N is the upper-bound on the number of nodes of a certain")
print("* \ttype inside a given zone. This value can be pre-computed.")
print("*")

# ---------------------------------------------------------------------------------------------------------------------
for channel in instance.channels:
    UB_on_C[channel] = len(channel.getAllowedDataFlow())
    Set_UB_on_C[channel] = range(1, UB_on_C[channel] + 1)
# Log the information concerning the variable.
print("*")
print("* UB_on_C [%s]" % len(UB_on_C))
print("* \tVariable UB_on_C is the upper-bound on the number of channels of a certain")
print("* \ttype. This upper-bound can be pre-computed")
print("*")

# ---------------------------------------------------------------------------------------------------------------------
for node in instance.nodes:
    for zone in instance.zones:
        N[node, zone] = m.addVar(lb=0.0, ub=UB_on_N[node, zone], obj=0.0, vtype=GRB.CONTINUOUS,
                                 name='N_%s_%s' % (node, zone))
# Log the information concerning the variable.
print("*")
print("* N [%s]" % len(N))
print("* \tVariable N identifies the number of deployed nodes of a certain type inside")
print("* \ta given zone. The upper-bound on this variable is equal to UB_on_N.")
print("*")

# ---------------------------------------------------------------------------------------------------------------------
for channel in instance.channels:
    C[channel] = m.addVar(lb=0.0, ub=UB_on_C[channel], obj=0.0, vtype=GRB.CONTINUOUS,
                          name='C_%s' % channel)
# Log the information concerning the variable.
print("*")
print("* C [%s]" % len(C))
print("* \tVariable C identifies the number of deployed channels of a certain type.")
print("* \tThe upper-bound on this variable is equal to UB_on_C.")
print("*")

# ---------------------------------------------------------------------------------------------------------------------
for node in instance.nodes:
    for zone in instance.zones:
        for nodeIndex in Set_UB_on_N[node, zone]:
            x[node, nodeIndex, zone] = m.addVar(lb=0.0, ub=1.0, obj=0.0, vtype=GRB.BINARY,
                                                name='x_%s_%s_%s' % (node, nodeIndex, zone))
# Log the information concerning the variable.
print("*")
print("* x [%s]" % len(x))
print("* \tVariable x identifies the number of nodes of a given type deployed inside")
print("* \ta given zone. If the variable x[n1,n1q,z1] is true, it means that")
print("* \tthere are n1q nodes of type n1 inside zone z1.")
print("*")

# ---------------------------------------------------------------------------------------------------------------------
for channel in instance.channels:
    for channelIndex in Set_UB_on_C[channel]:
        y[channel, channelIndex] = m.addVar(lb=0.0, ub=1.0, obj=0.0, vtype=GRB.BINARY,
                                            name='y_%s_%s' % (channel, channelIndex))
# Log the information concerning the variable.
print("*")
print("* y [%s]" % len(y))
print("* \tVariable y identifies the number of deployed channels for a given type of")
print("* \tchannel. In particular, if the variable y[c1,c1q] is true, it means that")
print("* \tthere are c1q channels of type c1 deployed inside the network.")
print("*")

# ---------------------------------------------------------------------------------------------------------------------
for dataflow in instance.dataflows:
    md[dataflow] = (dataflow.source.mobile or dataflow.target.mobile)

# Log the information concerning the variable.
print("*")
print("* md [%s]" % len(md))
print("* \tVariable md identifies if at least one of the tasks connected by a given")
print("* \tdata-flow is placed inside a mobile node. It is worth noting that if the")
print("* \tat least one of the tasks is actually a mobile task, the md variable needs")
print("* \tto be set to 1.")
print("*")

# ---------------------------------------------------------------------------------------------------------------------
for dataflow in instance.dataflows:
    for task in instance.tasks:
        gamma[dataflow, task] = not (dataflow.hasTask(task))
# Log the information concerning the variable.
print("*")
print("* gamma [%s]" % len(gamma))
print("* \tVariable gamma identifies if the given task is not the source or target")
print("* \ttask of the given data-flow.")
print("*")

# ---------------------------------------------------------------------------------------------------------------------
for task1 in instance.tasks:
    for task2 in instance.tasks:
        if task1 == task2:
            rho[task1, task2] = False
            rho[task2, task1] = False
        elif task1.zone != task2.zone:
            rho[task1, task2] = True
            rho[task2, task1] = True
        elif task1 < task2:
            rho[task1, task2] = m.addVar(lb=0.0, ub=1.0, obj=0.0, vtype=GRB.BINARY, name='rho_%s_%s' % (task1, task2))
            rho[task2, task1] = rho[task1, task2]
# Log the information concerning the variable.
print("*")
print("* rho [%s]" % len(rho))
print("* \tVariable rho identifies if two tasks are deployed inside two different")
print("* \tnodes.")
print("*")

# ---------------------------------------------------------------------------------------------------------------------
for task in instance.tasks:
    for node in task.getAllowedNode():
        for nodeIndex in Set_UB_on_N[node, task.zone]:
            w[task, node, nodeIndex] = m.addVar(lb=0.0, ub=1.0, obj=0.0, vtype=GRB.BINARY,
                                                name='w_%s_%s_%s' % (task, node, nodeIndex))
# Log the information concerning the variable.
print("*")
print("* w [%s]" % len(w))
print("* \tVariable w identifies if the given task has been deployed inside the ")
print("* \tgiven instance of the given type of node.")
print("*")

# ---------------------------------------------------------------------------------------------------------------------
for dataflow in instance.dataflows:
    for channel in dataflow.getAllowedChannel():
        for channelIndex in Set_UB_on_C[channel]:
            h[dataflow, channel, channelIndex] = m.addVar(lb=0.0, ub=1.0, obj=0.0, vtype=GRB.BINARY,
                                                          name='h_%s_%s_%s' % (dataflow, channel, channelIndex))
# Log the information concerning the variable.
print("*")
print("* h [%s]" % len(h))
print("* \tVariable h identifies if the given data-flow has been deployed inside the ")
print("* \tgiven instance of the given type of channel.")
print("*")

# ---------------------------------------------------------------------------------------------------------------------
for channel in instance.channels:
    for zone1 in instance.zones:
        for zone2 in instance.zones:
            q[channel, zone1, zone2] = (instance.contiguities.get((zone1, zone2, channel)).conductance > 0)
            if q[channel, zone1, zone2]:
                channel.setAllowedBetween(zone1, zone2)

# Log the information concerning the variable.
print("*")
print("* q [%s]" % len(q))
print("* \tVariable q is pre-computed and identifies if the given type of channel")
print("* \tcan be placed between the given pair of zones.")
print("*")

# ---------------------------------------------------------------------------------------------------------------------
for channel in instance.channels:
    for channelIndex in Set_UB_on_C[channel]:
        for zone1 in instance.zones:
            for zone2 in instance.zones:
                if zone1 <= zone2:
                    if q[channel, zone1, zone2]:
                        j[channel, channelIndex, zone1, zone2] = m.addVar(lb=0.0,
                                                                          ub=1.0,
                                                                          obj=0.0,
                                                                          vtype=GRB.BINARY,
                                                                          name='j_%s_%s_%s_%s' % (
                                                                              channel, channelIndex, zone1, zone2))
                        j[channel, channelIndex, zone2, zone1] = j[channel, channelIndex, zone1, zone2]
                    else:
                        j[channel, channelIndex, zone1, zone2] = False
                        j[channel, channelIndex, zone2, zone1] = False
# Log the information concerning the variable.
print("*")
print("* j [%s]" % len(j))
print("* \tVariable j identifies if the given instance of the given channel has ben ")
print("* \tactually placed between the given pair of zones.")
print("*")

# for dataflow in instance.dataflows:
#     for channel in dataflow.getAllowedChannel():
#         for channelIndex in Set_UB_on_C[channel]:
#             for node in dataflow.source.getAllowedNode():
#                 for nodeIndex in Set_UB_on_N[node, dataflow.source.zone]:
#                     sigma[channel, channelIndex, node, nodeIndex] = m.addVar(lb=0.0,
#                                                                              ub=1.0,
#                                                                              obj=0.0,
#                                                                              vtype=GRB.BINARY,
#                                                                              name='sigma_%s_%s_%s_%s' % (
#                                                                                  channel, channelIndex,
#                                                                                  node, nodeIndex))
#             for node in dataflow.target.getAllowedNode():
#                 for nodeIndex in Set_UB_on_N[node, dataflow.target.zone]:
#                     sigma[channel, channelIndex, node, nodeIndex] = m.addVar(lb=0.0,
#                                                                              ub=1.0,
#                                                                              obj=0.0,
#                                                                              vtype=GRB.BINARY,
#                                                                              name='sigma_%s_%s_%s_%s' % (
#                                                                                  channel, channelIndex,
#                                                                                  node, nodeIndex))
# print("*")
# print("* sigma [%s]" % len(sigma))
# print("* \tVariable sigma identifies if the given instance of a channel is ")
# print("* \tconnected with the instance of the given node.")
# print("*")
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

# ---------------------------------------------------------------------------------------------------------------------
print("* Constraint C1")
for node in instance.nodes:
    for zone in instance.zones:
        m.addConstr(lhs=N[node, zone],
                    sense=GRB.EQUAL,
                    rhs=quicksum(x[node, nodeIndex, zone] for nodeIndex in Set_UB_on_N[node, zone]),
                    name="define_N_%s_%s" % (node, zone))

# ---------------------------------------------------------------------------------------------------------------------
print("* Constraint C2")
for node in instance.nodes:
    for zone in instance.zones:
        for nodeIndex in Set_UB_on_N[node, zone]:
            m.addConstr(lhs=N[node, zone],
                        sense=GRB.GREATER_EQUAL,
                        rhs=nodeIndex * x[node, nodeIndex, zone],
                        name="mono_clones_of_N_%s_%s_%s" % (node, zone, nodeIndex))

# ---------------------------------------------------------------------------------------------------------------------
print("* Constraint C3")
for channel in instance.channels:
    m.addConstr(lhs=C[channel],
                sense=GRB.EQUAL,
                rhs=quicksum(y[channel, channelIndex] for channelIndex in Set_UB_on_C[channel]),
                name="define_C_%s" % channel)

# ---------------------------------------------------------------------------------------------------------------------
print("* Constraint C4")
for channel in instance.channels:
    for channelIndex in Set_UB_on_C[channel]:
        m.addConstr(lhs=C[channel],
                    sense=GRB.GREATER_EQUAL,
                    rhs=channelIndex * y[channel, channelIndex],
                    name="mono_clones_of_C_%s_%s" % (channel, channelIndex))

# ---------------------------------------------------------------------------------------------------------------------
print("* Constraint C5")
for task in instance.tasks:
    for node in task.getAllowedNode():
        for nodeIndex in Set_UB_on_N[node, task.zone]:
            m.addConstr(lhs=w[task, node, nodeIndex],
                        sense=GRB.LESS_EQUAL,
                        rhs=x[node, nodeIndex, task.zone],
                        name="codomain_existance_for_w_%s_%s_%s" % (task, node, nodeIndex))

# ---------------------------------------------------------------------------------------------------------------------
print("* Constraint C6")
for dataflow in instance.dataflows:
    for channel in dataflow.getAllowedChannel():
        for channelIndex in Set_UB_on_C[channel]:
            m.addConstr(lhs=h[dataflow, channel, channelIndex],
                        sense=GRB.LESS_EQUAL,
                        rhs=y[channel, channelIndex],
                        name="codomain_existance_for_h_%s_%s_%s" % (dataflow, channel, channelIndex))

# ---------------------------------------------------------------------------------------------------------------------
print("* Constraint C7")
for node in instance.nodes:
    for zone in instance.zones:
        for nodeIndex in Set_UB_on_N[node, zone]:
            m.addConstr(lhs=x[node, nodeIndex, zone],
                        sense=GRB.LESS_EQUAL,
                        rhs=quicksum(w[task, node, nodeIndex]
                                     for task in node.getAllowedTask()
                                     if task.zone == zone),
                        name="deactivate_unecessary_clones_of_x_%s_%s_%s" % (node, zone, nodeIndex))

# ---------------------------------------------------------------------------------------------------------------------
print("* Constraint C8")
for channel in instance.channels:
    for channelIndex in Set_UB_on_C[channel]:
        m.addConstr(lhs=y[channel, channelIndex],
                    sense=GRB.LESS_EQUAL,
                    rhs=quicksum(h[dataflow, channel, channelIndex]
                                 for dataflow in channel.getAllowedDataFlow()),
                    name="deactivate_unecessary_clones_of_y_%s_%s" % (channel, channelIndex))

# ---------------------------------------------------------------------------------------------------------------------
print("* Constraint C9")
for node in instance.nodes:
    for zone in instance.zones:
        for nodeIndex in Set_UB_on_N[node, zone]:
            m.addConstr(lhs=quicksum((task.size * w[task, node, nodeIndex])
                                     for task in node.getAllowedTask()
                                     if task.zone == zone),
                        sense=GRB.LESS_EQUAL,
                        rhs=node.size,
                        name="node_size_%s_%s" % (node, nodeIndex))

# ---------------------------------------------------------------------------------------------------------------------
print("* Constraint C10")
for channel in instance.channels:
    for channelIndex in Set_UB_on_C[channel]:
        m.addConstr(lhs=quicksum(((dataflow.size * h[dataflow, channel, channelIndex]) /
                                  instance.contiguities.get((dataflow.source.zone, dataflow.target.zone, channel)).conductance)
                                 for dataflow in channel.getAllowedDataFlow()),
                    sense=GRB.LESS_EQUAL,
                    rhs=channel.size,
                    name="channel_size_%s_%s" % (channel, channelIndex))

# ---------------------------------------------------------------------------------------------------------------------
print("* Constraint C11")
for task in instance.tasks:
    m.addConstr(lhs=quicksum(w[task, node, nodeIndex]
                             for node in task.getAllowedNode()
                             for nodeIndex in Set_UB_on_N[node, task.zone]),
                sense=GRB.EQUAL,
                rhs=1,
                name="unique_mapping_of_task_%s" % task)

# ---------------------------------------------------------------------------------------------------------------------
print("* Constraint C12")
for dataflow in instance.dataflows:
    if dataflow.source.zone != dataflow.target.zone:
        m.addConstr(lhs=quicksum(h[dataflow, channel, channelIndex]
                                 for channel in dataflow.getAllowedChannel()
                                 for channelIndex in Set_UB_on_C[channel]),
                    sense=GRB.EQUAL,
                    rhs=1,
                    name="unique_mapping_of_dataflow_%s" % dataflow)

print("* Constraint C13")
for dataflow in instance.dataflows:
    if dataflow.source.zone == dataflow.target.zone:
        m.addConstr(lhs=quicksum(h[dataflow, channel, channelIndex]
                                 for channel in dataflow.getAllowedChannel()
                                 for channelIndex in Set_UB_on_C[channel]),
                    sense=GRB.EQUAL,
                    rhs=rho[dataflow.source, dataflow.target],
                    name="unique_mapping_of_dataflow_%s" % dataflow)

# ---------------------------------------------------------------------------------------------------------------------
# print("* Constraint C14")
# for dataflow in instance.dataflows:
#     if dataflow.source.mobile:
#         m.addConstr(lhs=quicksum(w[dataflow.source, node, nodeIndex]
#                                  for node in dataflow.source.getAllowedNode()
#                                  if node.mobile
#                                  for nodeIndex in Set_UB_on_N[node, dataflow.source.zone]),
#                     sense=GRB.LESS_EQUAL,
#                     rhs=md[dataflow],
#                     name="Define_md_for_dataflow_%s" % dataflow)
#
# print("* Constraint C15")
# for dataflow in instance.dataflows:
#     if dataflow.target.mobile:
#         m.addConstr(lhs=quicksum(w[dataflow.target, node, nodeIndex]
#                                  for node in dataflow.target.getAllowedNode()
#                                  if node.mobile
#                                  for nodeIndex in Set_UB_on_N[node, dataflow.target.zone]),
#                     sense=GRB.LESS_EQUAL,
#                     rhs=md[dataflow],
#                     name="Define_md_for_dataflow_%s" % dataflow)

# ---------------------------------------------------------------------------------------------------------------------
# print("* Constraint C16")
# for dataflow in instance.dataflows:
#     if dataflow.source.zone != dataflow.target.zone:
#         m.addConstr(lhs=md[dataflow],
#                     sense=GRB.GREATER_EQUAL,
#                     rhs=quicksum(h[dataflow, channel, channelIndex]
#                                  for channel in dataflow.getAllowedChannel()
#                                  if channel.wireless
#                                  for channelIndex in Set_UB_on_C[channel]),
#                     name="Unique_mapping_of_dataflow_%s_wrt_wireless_channels" % dataflow)
#
# print("* Constraint C17")
# for dataflow in instance.dataflows:
#     if dataflow.source.zone == dataflow.target.zone:
#         m.addConstr(lhs=rho[dataflow.source, dataflow.target] - 1,
#                     sense=GRB.GREATER_EQUAL,
#                     rhs=quicksum(h[dataflow, channel, channelIndex]
#                                  for channel in dataflow.getAllowedChannel()
#                                  if channel.wireless
#                                  for channelIndex in Set_UB_on_C[channel]),
#                     name="Unique_mapping_of_dataflow_%s_wrt_wireless_channels" % dataflow)

# ---------------------------------------------------------------------------------------------------------------------
print("* Constraint C18")
for task1 in instance.tasks:
    for task2 in instance.tasks:
        if (task1 == task2) or (task1.zone != task2.zone):
            continue
        for node1 in task1.getAllowedNode():
            for node2 in task2.getAllowedNode():
                for node1Index in Set_UB_on_N[node1, task1.zone]:
                    for node2Index in Set_UB_on_N[node2, task2.zone]:
                        if [node1, node1Index] == [node2, node2Index]:
                            continue
                        m.addConstr(lhs=rho[task1, task2],
                                    sense=GRB.GREATER_EQUAL,
                                    rhs=w[task1, node1, node1Index] + w[task2, node2, node2Index] - 1,
                                    name="Task_mapping_in_different_nodes_of_%s_%s" % (task1, task2))

# ---------------------------------------------------------------------------------------------------------------------
print("* Constraint C19")
for channel in instance.channels:
    if channel.wireless:
        continue
    for channelIndex in Set_UB_on_C[channel]:
        for dataflow1 in channel.getAllowedDataFlow():
            for dataflow2 in channel.getAllowedDataFlow():
                if dataflow1 >= dataflow2:
                    continue
                if not (gamma[dataflow1, dataflow2.source] or gamma[dataflow1, dataflow2.target]):
                    continue
                m.addConstr(lhs=h[dataflow1, channel, channelIndex] + h[dataflow2, channel, channelIndex],
                            sense=GRB.LESS_EQUAL,
                            rhs=1,
                            name="Cabled_channel_%s_%s_serves_only_two_nodes_%s_%s" % (
                                channel, channelIndex, dataflow1, dataflow2))

# ---------------------------------------------------------------------------------------------------------------------
print("* Constraint C20")
for dataflow in instance.dataflows:
    for task in instance.tasks:
        if not gamma[dataflow, task]:
            continue
        m.addConstr(lhs=rho[task, dataflow.source] +
                        rho[task, dataflow.target] +
                        rho[dataflow.source, dataflow.target] - 2,
                    sense=GRB.LESS_EQUAL,
                    rhs=1,
                    name="Define_gamma_variable_for_%s_%s_%s" % (task, dataflow.source, dataflow.target))

# ---------------------------------------------------------------------------------------------------------------------
print("* Constraint C21")
for zone1 in instance.zones:
    for zone2 in instance.zones:
        for channel in instance.channels:
            if channel.wireless:
                continue
            for channelIndex in Set_UB_on_C[channel]:
                for dataflow in channel.getAllowedDataFlow():
                    if not dataflow.concernsZones(zone1, zone2):
                        continue
                    m.addConstr(lhs=j[channel, channelIndex, zone1, zone2],
                                sense=GRB.GREATER_EQUAL,
                                rhs=h[dataflow, channel, channelIndex] * q[channel, zone1, zone2],
                                name="Cabled_channel_%s_%s_between_zones_%s_%s" % (
                                    channel, channelIndex, zone1, zone2))

# ---------------------------------------------------------------------------------------------------------------------
print("* Constraint C22")
for channel in instance.channels:
    if not channel.wireless:
        continue
    for channelIndex in Set_UB_on_C[channel]:
        for dataflow1 in channel.getAllowedDataFlow():
            for dataflow2 in channel.getAllowedDataFlow():
                if dataflow1 >= dataflow2:
                    continue
                m.addConstr(lhs=h[dataflow1, channel, channelIndex] + h[dataflow2, channel, channelIndex],
                            sense=GRB.LESS_EQUAL,
                            rhs=(1 +
                                 q[channel, dataflow1.source.zone, dataflow2.source.zone] *
                                 q[channel, dataflow1.source.zone, dataflow2.target.zone] *
                                 q[channel, dataflow1.target.zone, dataflow2.source.zone] *
                                 q[channel, dataflow1.target.zone, dataflow2.target.zone]),
                            name="Wireless_with_df_%s_%s" % (dataflow1.label, dataflow2.label))

# ---------------------------------------------------------------------------------------------------------------------
# print("* Constraint C23")
# for dataflow in instance.dataflows:
#     for channel in dataflow.getAllowedChannel():
#         for channelIndex in Set_UB_on_C[channel]:
#             for node in dataflow.source.getAllowedNode():
#                 for nodeIndex in Set_UB_on_N[node, dataflow.source.zone]:
#                     m.addConstr(lhs=sigma[channel, channelIndex, node, nodeIndex],
#                                 sense=GRB.LESS_EQUAL,
#                                 rhs=h[dataflow, channel, channelIndex] * w[dataflow.source, node, nodeIndex],
#                                 name="channel_%s_%s_connection_with_%s_%s" % (channel, channelIndex, node, nodeIndex))
#             for node in dataflow.target.getAllowedNode():
#                 for nodeIndex in Set_UB_on_N[node, dataflow.target.zone]:
#                     m.addConstr(lhs=sigma[channel, channelIndex, node, nodeIndex],
#                                 sense=GRB.LESS_EQUAL,
#                                 rhs=h[dataflow, channel, channelIndex] * w[dataflow.target, node, nodeIndex],
#                                 name="channel_%s_%s_connection_with_%s_%s" % (channel, channelIndex, node, nodeIndex))

# ---------------------------------------------------------------------------------------------------------------------
# print("* Constraint C24")
# for dataflow in instance.dataflows:
#     for channel in dataflow.getAllowedChannel():
#         for channelIndex in Set_UB_on_C[channel]:
#             m.addConstr(lhs=quicksum(sigma[channel, channelIndex, node, nodeIndex]
#                                      for node in dataflow.source.getAllowedNode()
#                                      for nodeIndex in Set_UB_on_N[node, dataflow.source.zone]) +
#                             quicksum(sigma[channel, channelIndex, node, nodeIndex]
#                                      for node in dataflow.target.getAllowedNode()
#                                      for nodeIndex in Set_UB_on_N[node, dataflow.target.zone]),
#                         sense=GRB.LESS_EQUAL,
#                         rhs=channel.max_conn,
#                         name="channel_%s_%s_max_connections" % (channel, channelIndex))
# END - The constraints section - END

m.update()

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
                 for node in instance.nodes
                 for zone in instance.zones
                 for nodeIndex in Set_UB_on_N[node, zone]) +
        quicksum(y[channel, channelIndex] * channel.cost
                 for channel in instance.channels
                 for channelIndex in Set_UB_on_C[channel]) +
        quicksum(j[channel, channelIndex, zone1, zone2] * instance.contiguities.get((zone1, zone2, channel)).deploymentCost
                 for zone1 in instance.zones
                 for zone2 in instance.zones
                 for channel in instance.channels
                 if not channel.wireless
                 if channel.isAllowedBetween(zone1, zone2)
                 for channelIndex in Set_UB_on_C[channel]),
        GRB.MINIMIZE
    )
    m.update()
elif OPTIMIZATION == 2:
    print("*    Energy Consumption Minimization")
    # Energy Consumption Minimization:
    #   The second optimization objective is to minimize the global energy consumption of the network.
    m.setObjective(
        quicksum(x[node, nodeIndex, zone] * node.energy
                 for node in instance.nodes
                 for zone in instance.zones
                 for nodeIndex in Set_UB_on_N[node, zone]) +
        quicksum(w[task, node, nodeIndex] * node.task_energy * task.size
                 for task in instance.tasks
                 for node in task.getAllowedNode()
                 for nodeIndex in Set_UB_on_N[node, task.zone]) +
        quicksum(y[channel, channelIndex] * channel.energy
                 for channel in instance.channels
                 for channelIndex in Set_UB_on_C[channel]) +
        quicksum(h[dataflow, channel, channelIndex] * channel.df_energy * dataflow.size /
                 instance.contiguities.get((dataflow.source.zone, dataflow.target.zone, channel)).conductance
                 for dataflow in instance.dataflows
                 for channel in dataflow.getAllowedChannel()
                 for channelIndex in Set_UB_on_C[channel]),
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
                 instance.contiguities.get((dataflow.source.zone, dataflow.target.zone, channel)).conductance
                 for dataflow in instance.dataflows
                 for channel in dataflow.getAllowedChannel()
                 for channelIndex in Set_UB_on_C[channel]),
        GRB.MINIMIZE
    )
    m.update()
elif OPTIMIZATION == 4:
    print("*    Error Rate Minimization")
    # Error Rate Minimization:
    #   The optimization objective is to minimize the global error rate of the network.
    m.setObjective(
        quicksum(channel.error * h[dataflow, channel, channelIndex] /
                 instance.contiguities.get((dataflow.source.zone, dataflow.target.zone, channel)).conductance
                 for dataflow in instance.dataflows
                 for channel in dataflow.getAllowedChannel()
                 for channelIndex in Set_UB_on_C[channel]),
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
                    instance.contiguities.get((dataflow.source.zone, dataflow.target.zone, channel)).conductance) +
                (channel.error * h[dataflow, channel, channelIndex]) / (
                    instance.contiguities.get((dataflow.source.zone, dataflow.target.zone, channel)).conductance)
            ) for dataflow in instance.dataflows for channel in dataflow.getAllowedChannel() for channelIndex in
            Set_UB_on_C[channel]
        ),
        GRB.MINIMIZE
    )
    m.update()

print("*******************************************************************************")
print("* Starting optimization...")

# ---------------------------------------------------------------------------------------------------------------------
# ---------------------------------------------------------------------------------------------------------------------
# SOLVER PARAMETERS
# ---------------------------------------------------------------------------------------------------------------------

# ---------------------------------------------------------------------------------------------------------------------
# Controls the presolve level.
#
# A value of -1 corresponds to an automatic setting.
# Other options are off (0), conservative (1), or aggressive (2). More aggressive application of presolve
# takes more time, but can sometimes lead to a significantly tighter model.
m.setParam("Presolve", 2)

# ---------------------------------------------------------------------------------------------------------------------
# Algorithm used to solve continuous models or the root node of a MIP model.
# Type:	int
# Default value:	-1
# Minimum value:	-1
# Maximum value:	4
#
# Options are: -1=automatic, 0=primal simplex, 1=dual simplex, 2=barrier, 3=concurrent, 4=deterministic concurrent.
# In the current release, the default Automatic (-1) setting will typically choose
# non-deterministic concurrent (Method=3) for an LP, barrier (Method=2) for a QP or QCP,
# and dual (Method=1) for the MIP root node. Only the simplex and barrier algorithms are available for continuous
# QP models. Only primal and dual simplex are available for solving the root of an MIQP model.
# Only barrier is available for continuous QCP models.
# Concurrent optimizers run multiple solvers on multiple threads simultaneously, and choose the one that
# finishes first. Deterministic concurrent (Method=4) gives the exact same result each time,
# while Method=3 is often faster but can produce different optimal bases when run multiple times.
m.setParam("Method", 3)

# Optimization start.
optimization_timer_begin = time.time()

# Compute optimal solution
m.optimize()

# Optimization end.
optimization_timer_end = time.time()

used_memory = GetMemoryUsage()
used_cpu = psutil.cpu_percent(interval=1)

outcome = open("result.txt", 'a+')
outcome_txt = "SUCCESS"
outfile = open(str(argv[1]).replace("/", "_"), 'a+')

# print(solution
if m.status == GRB.status.OPTIMAL:
    outfile.write("Optimal objective: %g\n" % m.objVal)
    outfile.write("*******************************************************************************\n")
    outfile.write('# Optimal Solution\n')
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
    outfile.write('# List of activated nodes:\n')
    SolN = m.getAttr('x', N)
    for zone in instance.zones:
        for node in instance.nodes:
            if SolN[node, zone] > 0:
                TotalCostNodes += node.cost * SolN[node, zone]
                TotalEnergyNodes += node.energy * SolN[node, zone]
                outfile.write('    In zone %s, use %g nodes of type %s\n' % (zone, SolN[node, zone], node))

    outfile.write('# List of activated channels:\n')
    SolC = m.getAttr('x', C)
    for channel in instance.channels:
        if SolC[channel] > 0:
            if channel.wireless:
                TotalCostWirls += channel.cost * SolC[channel]
            else:
                TotalCostCable += channel.cost * SolC[channel]
            TotalEnergyChannel += channel.energy * SolC[channel]
            outfile.write('    Use %g channels of type %s\n' % (SolC[channel], channel))

    outfile.write('# Tasks allocation:\n')
    SolW = m.getAttr('x', w)
    for zone in instance.zones:
        for task in instance.tasks:
            if task.zone == zone:
                for node in task.getAllowedNode():
                    for nodeIndex in Set_UB_on_N[node, zone]:
                        if SolW[task, node, nodeIndex]:
                            TotalEnergyNodesUsage += (node.task_energy * task.size)
                            task.setDeployedIn(node, nodeIndex, zone)
                            outfile.write('    Task %-24s inside node Zone%s.%s.%s\n'
                                          % (task, zone, node, nodeIndex))

    outfile.write('# Data-Flows allocation:\n')
    SolH = m.getAttr('x', h)
    for dataflow in instance.dataflows:
        for channel in dataflow.getAllowedChannel():
            contiguity = instance.contiguities.get((dataflow.source.zone, dataflow.target.zone, channel))
            for channelIndex in Set_UB_on_C[channel]:
                if SolH[dataflow, channel, channelIndex]:
                    dataflow.setDeployedIn(channel, channelIndex)
                    TotalEnergyChannelUsage += (channel.df_energy * dataflow.size)
                    if channel.wireless:
                        TotalDelayWirls += (channel.delay / contiguity.conductance)
                        TotalErrorRateWirls += (channel.error / contiguity.conductance)
                    else:
                        TotalDelayCable += (channel.delay / contiguity.conductance)
                        TotalErrorRateCable += (channel.error / contiguity.conductance)
                    outfile.write('    Dataflow %-24s inside channel %s.%s\n' % (dataflow, channel, channelIndex))
            del contiguity

    SolY = m.getAttr('x', y)
    for channel in dataflow.getAllowedChannel():
        if not channel.wireless:
            for channelIndex in Set_UB_on_C[channel]:
                if SolY[channel, channelIndex]:
                    deploymentCost = sys.maxint
                    for dataflow in channel.getAllowedDataFlow():
                        contiguity = instance.contiguities.get((dataflow.source.zone, dataflow.target.zone, channel))
                        if SolH[dataflow, channel, channelIndex]:
                            deploymentCost = contiguity.deploymentCost
                        del contiguity
                    if channel.wireless:
                        TotalCostWirls += deploymentCost
                    else:
                        TotalCostCable += deploymentCost
                    del deploymentCost

    outfile.write("*                                  \n")
    outfile.write("* Final Statistics:                \n")
    outfile.write("*     Economic Cost      : %s      \n" % (TotalCostNodes + TotalCostWirls + TotalCostCable))
    outfile.write("*         Nodes Deployment     : %s\n" % TotalCostNodes)
    outfile.write("*         Wireless Channels    : %s\n" % TotalCostWirls)
    outfile.write("*         Cable    Channels    : %s\n" % TotalCostCable)
    outfile.write("*     Energy Consumption : %s      \n" % (
        TotalEnergyNodes + TotalEnergyNodesUsage + TotalEnergyChannel + TotalEnergyChannelUsage))
    outfile.write("*         Nodes Power          : %s\n" % TotalEnergyNodes)
    outfile.write("*         Nodes Power Usage    : %s\n" % TotalEnergyNodesUsage)
    outfile.write("*         Channels Power       : %s\n" % TotalEnergyChannel)
    outfile.write("*         Channels Power Usage : %s\n" % TotalEnergyChannelUsage)
    outfile.write("*     Total Delay        : %s      \n" % (TotalDelayWirls + TotalDelayCable))
    outfile.write("*         Wireless Channels    : %s\n" % TotalDelayWirls)
    outfile.write("*         Cable    Channels    : %s\n" % TotalDelayCable)
    outfile.write("*     Total Error        : %s      \n" % (TotalErrorRateWirls + TotalErrorRateCable))
    outfile.write("*         Wireless Channels    : %s\n" % TotalErrorRateWirls)
    outfile.write("*         Cable    Channels    : %s\n" % TotalErrorRateCable)

    checker = NetworkChecker(instance.nodes,
                             instance.channels,
                             instance.zones,
                             instance.contiguities,
                             instance.tasks,
                             instance.dataflows,
                             SolN,
                             SolC,
                             SolW,
                             SolH,
                             Set_UB_on_C,
                             Set_UB_on_N,
                             outfile)
    if not checker.checkNetwork():
        outcome_txt = "FAILED"

elif m.status == GRB.Status.INF_OR_UNBD:
    outfile.write('Model is infeasible or unbounded\n')
    outcome_txt = "FAILED"
    m.computeIIS()
    m.write("model.ilp")

elif m.status == GRB.Status.INFEASIBLE:
    outfile.write('Model is infeasible\n')
    outcome_txt = "FAILED"
    m.computeIIS()
    m.write("model.ilp")

elif m.status == GRB.Status.UNBOUNDED:
    outfile.write('Model is unbounded\n')
    outcome_txt = "FAILED"

else:
    outfile.write('Optimization ended with status %d\n' % m.status)
    outcome_txt = "FAILED"

if XML_GENERATION == 1:
    print("*##########################################")
    print("* Generating UML for Scilab...")
    umlPrinter = UmlForScilabPrinter(instance.nodes,
                                     instance.channels,
                                     instance.zones,
                                     instance.contiguities,
                                     instance.tasks,
                                     instance.dataflows,
                                     SolN,
                                     SolC,
                                     SolW,
                                     SolH,
                                     Set_UB_on_C,
                                     Set_UB_on_N)
    umlPrinter.printNetwork()
    print("*##########################################")
    print("* Generating Technological Library...")
    techLibPrinter = TechLibPrinter(instance.nodes, instance.channels)
    techLibPrinter.printTechLib()

if SCNSL_GENERATION == 1:
    scnslPrinter = ScnslGenerator(instance.nodes, instance.channels, instance.zones, instance.contiguities, instance.tasks, instance.dataflows,
                                  SolN,
                                  SolC,
                                  SolW, SolH, Set_UB_on_C, Set_UB_on_N)
    scnslPrinter.printScnslNetwork("main.cc")

elapsed_parse = parse_timer_end - parse_timer_begin
elapsed_struc = structure_timer_end - structure_timer_begin
elapsed_const = constraints_timer_end - constraints_timer_begin
elapsed_optim = optimization_timer_end - optimization_timer_begin
elapsed_total = elapsed_parse + elapsed_struc + elapsed_const + elapsed_optim

# Print elapsed times.
outfile.write("*\n")
outfile.write("*##########################################\n")
outfile.write("* Statistics...\n")
outfile.write("*\n")
outfile.write("*    File parsing           : %s s\n" % elapsed_parse)
outfile.write("*    Structure creation     : %s s\n" % elapsed_struc)
outfile.write("*    Constraints definition : %s s\n" % elapsed_const)
outfile.write("*    Optimization           : %s s\n" % elapsed_optim)
outfile.write("*    Total : %s s\n" % elapsed_total)
outfile.write("*##########################################\n")

outcome.write("[%-36s] OBJ-%d %-12s |   %8.6s s | %8.6s s | %8.6s s | %8.6s s | %8.6s s | %16.14s Mb | %8.4s |\n" %
              (argv[1], OPTIMIZATION, outcome_txt, elapsed_parse, elapsed_struc, elapsed_const, elapsed_optim,
               elapsed_total, used_memory, used_cpu))
outcome.flush()
outcome.close()

outfile.flush()
outfile.close()

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

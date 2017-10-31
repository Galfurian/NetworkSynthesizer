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

# ---------------------------------------------------------------------------------------------------------------------
# Synthesizer arguments
OPTIMIZATION = 1
XML_GENERATION = 0
SCNSL_GENERATION = 0
VERBOSE = 1

# Outcome file
outcome = open("result.txt", 'a+')
outcome_txt = "SUCCESS"

# Elapsed time variables
parse_timer_begin = parse_timer_end = 0
structure_timer_begin = structure_timer_end = 0
constraints_timer_begin = constraints_timer_end = 0
optimization_timer_begin = optimization_timer_end = 0
elapsed_parse = 0
elapsed_struc = 0
elapsed_const = 0
elapsed_optim = 0
elapsed_total = 0

# Used memory
used_memory = 0

# Optimization Results
# Economic Cost
total_cost_cable = 0
total_cost_wirls = 0
total_cost_nodes = 0
# Energy Consumption
total_energy_nodes = 0
total_energy_nodes_usage = 0
total_energy_channels = 0
total_energy_channels_usage = 0
# Communication Delay
total_delay_cable = 0
total_delay_wireless = 0
# Error Rate
total_error_cable = 0
total_error_wireless = 0


# ---------------------------------------------------------------------------------------------------------------------
def QuitSynthesizer(_outcome_txt=outcome_txt):
    if _outcome_txt:
        outcome_txt = _outcome_txt

    elapsed_parse = parse_timer_end - parse_timer_begin
    elapsed_struc = structure_timer_end - structure_timer_begin
    elapsed_const = constraints_timer_end - constraints_timer_begin
    elapsed_optim = optimization_timer_end - optimization_timer_begin
    elapsed_total = elapsed_parse + elapsed_struc + elapsed_const + elapsed_optim

    outcome.write(
        "[%-42s] OBJ-%d %-7s | %8.6s s| %8.6s s| %8.6s s| %8.6s s| %8.6s s| %8.6s Mb| %8.6s | %8.6s | %8.6s | %8.6s |\n" %
        (argv[1] if argc > 1 else "None",
         OPTIMIZATION,
         outcome_txt,
         elapsed_parse, elapsed_struc, elapsed_const, elapsed_optim, elapsed_total,
         used_memory,
         total_cost_nodes + total_cost_wirls + total_cost_cable,
         total_energy_nodes + total_energy_nodes_usage + total_energy_channels + total_energy_channels_usage,
         total_delay_wireless + total_delay_cable,
         total_error_wireless + total_error_cable))
    outcome.flush()
    outcome.close()
    exit(0)


# ---------------------------------------------------------------------------------------------------------------------
def Separator():
    print("*******************************************************************************")


# ---------------------------------------------------------------------------------------------------------------------
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
    QuitSynthesizer("FAILED")


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
if not instance.load_node_catalog(argv[2]):
    QuitSynthesizer("FAILED")
Separator()

# ---------------------------------------------------------------------------------------------------------------------
Separator()
print("* READING CHANNELSs CATALOG FILE")
Separator()
if not instance.load_channel_catalog(argv[3]):
    QuitSynthesizer("FAILED")
Separator()

# ---------------------------------------------------------------------------------------------------------------------
Separator()
print("* READING INPUT INSTANCE FILE")
Separator()
if not instance.load_input_instance(argv[1]):
    QuitSynthesizer("FAILED")
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
if not instance.perform_precheck():
    QuitSynthesizer("FAILED")
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
for node, zone in itertools.product(instance.nodes, instance.zones):
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
for node, zone in itertools.product(instance.nodes, instance.zones):
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
for node, zone in itertools.product(instance.nodes, instance.zones):
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
for dataflow, task in itertools.product(instance.dataflows, instance.tasks):
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
    for zone1, zone2 in itertools.combinations_with_replacement(instance.zones, 2):
        q[channel, zone1, zone2] = (instance.contiguities.get((zone1, zone2, channel)).conductance > 0)
        q[channel, zone2, zone1] = q[channel, zone1, zone2]
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
        for zone1, zone2 in itertools.combinations_with_replacement(instance.zones, 2):
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
for node, zone in itertools.product(instance.nodes, instance.zones):
    m.addConstr(lhs=N[node, zone],
                sense=GRB.EQUAL,
                rhs=quicksum(x[node, nodeIndex, zone] for nodeIndex in Set_UB_on_N[node, zone]),
                name="define_N_%s_%s" % (node, zone))

# ---------------------------------------------------------------------------------------------------------------------
print("* Constraint C2")
for node, zone in itertools.product(instance.nodes, instance.zones):
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
for node, zone in itertools.product(instance.nodes, instance.zones):
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
for node, zone in itertools.product(instance.nodes, instance.zones):
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
                                  instance.contiguities.get(
                                      (dataflow.source.zone, dataflow.target.zone, channel)).conductance)
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
print("* Constraint C18")
for task1, task2 in itertools.combinations(instance.tasks, 2):
    if task1.zone != task2.zone:
        continue
    for node1, node2 in itertools.product(task1.getAllowedNode(), task2.getAllowedNode()):
        for node1Index, node2Index in itertools.product(Set_UB_on_N[node1, task1.zone], Set_UB_on_N[node2, task2.zone]):
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
        for dataflow1, dataflow2 in itertools.combinations(channel.getAllowedDataFlow(), 2):
            if not (gamma[dataflow1, dataflow2.source] or gamma[dataflow1, dataflow2.target]):
                continue
            m.addConstr(lhs=h[dataflow1, channel, channelIndex] + h[dataflow2, channel, channelIndex],
                        sense=GRB.LESS_EQUAL,
                        rhs=1,
                        name="Cabled_channel_%s_%s_serves_only_two_nodes_%s_%s" % (
                            channel, channelIndex, dataflow1, dataflow2))

# ---------------------------------------------------------------------------------------------------------------------
print("* Constraint C20")
for dataflow, task in itertools.product(instance.dataflows, instance.tasks):
    if gamma[dataflow, task]:
        m.addConstr(
            lhs=rho[task, dataflow.source] + rho[task, dataflow.target] + rho[dataflow.source, dataflow.target] - 2,
            sense=GRB.LESS_EQUAL,
            rhs=1,
            name="Define_gamma_variable_for_%s_%s_%s" % (task, dataflow.source, dataflow.target))

# ---------------------------------------------------------------------------------------------------------------------
print("* Constraint C21")
for zone1, zone2 in itertools.combinations(instance.zones, 2):
    for channel in instance.channels:
        if channel.wireless:
            continue
        if not channel.isAllowedBetween(zone1, zone2):
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
    if channel.wireless:
        for channelIndex in Set_UB_on_C[channel]:
            for dataflow1, dataflow2 in itertools.combinations(channel.getAllowedDataFlow(), 2):
                m.addConstr(lhs=h[dataflow1, channel, channelIndex] + h[dataflow2, channel, channelIndex],
                            sense=GRB.LESS_EQUAL,
                            rhs=(1 +
                                 q[channel, dataflow1.source.zone, dataflow2.source.zone] *
                                 q[channel, dataflow1.source.zone, dataflow2.target.zone] *
                                 q[channel, dataflow1.target.zone, dataflow2.source.zone] *
                                 q[channel, dataflow1.target.zone, dataflow2.target.zone]),
                            name="Wireless_with_df_%s_%s" % (dataflow1.label, dataflow2.label))

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
        quicksum(
            x[node, nodeIndex, zone] * (node.cost + node.energy * node.energy_cost)
            for node, zone in itertools.product(instance.nodes, instance.zones)
            for nodeIndex in Set_UB_on_N[node, zone]) +
        quicksum(
            w[task, node, nodeIndex] * node.task_energy * task.size * node.energy_cost
            for task in instance.tasks
            for node in task.getAllowedNode()
            for nodeIndex in Set_UB_on_N[node, task.zone]) +
        quicksum(
            y[channel, channelIndex] * (channel.cost + channel.energy * channel.energy_cost)
            for channel in instance.channels
            for channelIndex in Set_UB_on_C[channel]) +
        quicksum(
            j[channel, channelIndex, zone1, zone2] * instance.contiguities.get((zone1, zone2, channel)).deploymentCost
            for zone1, zone2 in itertools.combinations(instance.zones, 2)
            for channel in instance.channels if channel.isAllowedBetween(zone1, zone2) if not channel.wireless
            for channelIndex in Set_UB_on_C[channel]) +
        quicksum(
            h[dataflow, channel, channelIndex] * channel.df_energy * dataflow.size * channel.energy_cost /
            instance.contiguities.get((dataflow.source.zone, dataflow.target.zone, channel)).conductance
            for dataflow in instance.dataflows
            for channel in dataflow.getAllowedChannel()
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
                 for node, zone in itertools.product(instance.nodes, instance.zones)
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
# m.setParam("Presolve", 2)

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
# m.setParam("Method", 3)

# MIPGap
#
# Relative MIP optimality gap
# Type:	double
# Default value:	1e-4
# Minimum value:	0
# Maximum value:	Infinity
# The MIP solver will terminate (with an optimal result) when the relative gap between the lower and upper objective bound is less than MIPGap times the upper bound.
# m.setParam("MIPGap", 1e-4)

# MIPGapAbs
#
# Absolute MIP optimality gap
# Type:	double
# Default value:	1e-10
# Minimum value:	0
# Maximum value:	Infinity
# The MIP solver will terminate (with an optimal result) when the absolute gap between the lower and upper objective bound is less than MIPGapAbs.
# m.setParam("MIPGapAbs", 1e-10)

# OptimalityTol
#
# Dual feasibility tolerance
# Type:	double
# Default value:	1e-6
# Minimum value:	1e-9
# Maximum value:	1e-2
# Reduced costs must all be smaller than OptimalityTol in the improving direction in order for a model to be declared optimal.
# m.setParam("OptimalityTol", 1e-5)

# FeasibilityTol
#
# Primal feasibility tolerance
# Type:	double
# Default value:	1e-6
# Minimum value:	1e-9
# Maximum value:	1e-2
# All constraints must be satisfied to a tolerance of FeasibilityTol. Tightening this tolerance can produce smaller constraint violations, but for numerically challenging models it can sometimes lead to much larger iteration counts.
# m.setParam("FeasibilityTol", 1e-5)

# NumericFocus
#
# Numerical focus
# Type:	int
# Default value:	0
# Minimum value:	0
# Maximum value:	3
# The NumericFocus parameter controls the degree to which the code attempts to detect and manage numerical issues. The default setting (0) makes an automatic choice, with a slight preference for speed. Settings 1-3 increasingly shift the focus towards being more careful in numerical computations. With higher values, the code will spend more time checking the numerical accuracy of intermediate results, and it will employ more expensive techniques in order to avoid potential numerical issues.
# m.setParam("NumericFocus", 2)

# Optimization start.
optimization_timer_begin = time.time()

# r = m.relax()
# r.write("gurobi.relax-nopre.rew")
# p = m.presolve()
# r = p.relax()
# r.write("gurobi.relax-pre.rew")
# m.reset()
# m.Params.Aggregate = 0
# p = m.presolve()
# r = p.relax()
# r.write("gurobi.relax-agg0.rew")
# m.feasRelaxS(0, True, False, True)

# m.printStats()

# Compute optimal solution
m.optimize()

# Optimization end.
optimization_timer_end = time.time()

m.printQuality()

used_memory = GetMemoryUsage()

outfile = open(str(argv[1]).replace("/", "_"), 'a+')

# print(solution
if m.status == GRB.status.OPTIMAL:

    instance.sol_N = m.getAttr('x', N)
    instance.sol_C = m.getAttr('x', C)

    instance.sol_x = m.getAttr('x', x)
    instance.sol_y = m.getAttr('x', y)

    instance.sol_w = m.getAttr('x', w)
    instance.sol_h = m.getAttr('x', h)

    # -----------------------------------------------------------------------------------------------------------------
    for zone in instance.zones:
        for node in instance.nodes:
            # Update COST
            total_cost_nodes += instance.sol_N[node, zone] * (node.cost + node.energy * node.energy_cost)
            # Update ENERGY
            total_energy_nodes += instance.sol_N[node, zone] * node.energy
            # Considers also the tasks.
            for task in node.getAllowedTask():
                if task.zone == zone:
                    for nodeIndex in Set_UB_on_N[node, zone]:
                        if instance.sol_w[task, node, nodeIndex]:
                            # Update COST * NODE
                            total_cost_nodes += (node.task_energy * task.size * node.energy_cost)
                            # Update ENERGY * NODE
                            total_energy_nodes_usage += (node.task_energy * task.size)

    for channel in instance.channels:
        # Update COST
        if channel.wireless:
            total_cost_wirls += instance.sol_C[channel] * (channel.cost + channel.energy * channel.energy_cost)
        else:
            total_cost_cable += instance.sol_C[channel] * (channel.cost + channel.energy * channel.energy_cost)
        # Update ENERGY
        total_energy_channels += instance.sol_C[channel] * channel.energy
        # Considers also the dataflows.
        for dataflow in channel.getAllowedDataFlow():
            conductance = instance.contiguities.get((dataflow.source.zone, dataflow.target.zone, channel)).conductance
            for channelIndex in Set_UB_on_C[channel]:
                # Update the general case
                if instance.sol_h[dataflow, channel, channelIndex]:
                    # Update COST * DATAFLOW, DELAY * DATAFLOW, ERROR * DATAFLOW
                    if channel.wireless:
                        total_cost_wirls += (channel.df_energy * dataflow.size * channel.energy_cost) / conductance
                        total_delay_wireless += (channel.delay / conductance)
                        total_error_wireless += (channel.error / conductance)
                    else:
                        total_cost_cable += (channel.df_energy * dataflow.size * channel.energy_cost) / conductance
                        total_delay_cable += (channel.delay / conductance)
                        total_error_cable += (channel.error / conductance)
                    # Update ENERGY * DATAFLOW
                    total_energy_channels_usage += (channel.df_energy * dataflow.size)
                # Update also the DEPLOYMENT COST
                if not channel.wireless and instance.sol_y[channel, channelIndex]:
                    deploymentCost = sys.maxint
                    for dataflow in channel.getAllowedDataFlow():
                        contiguity = instance.contiguities.get((dataflow.source.zone, dataflow.target.zone, channel))
                        if instance.sol_h[dataflow, channel, channelIndex]:
                            deploymentCost = contiguity.deploymentCost
                    # Update COST * DEPLOYMENT
                    total_cost_cable += deploymentCost

    # -----------------------------------------------------------------------------------------------------------------
    outfile.write("Optimal objective: %g\n" % m.objVal)
    outfile.write("*******************************************************************************\n")
    outfile.write("# Optimal Solution\n")
    outfile.write("# List of activated nodes:\n")
    for zone in instance.zones:
        for node in instance.nodes:
            if instance.sol_N[node, zone]:
                outfile.write("\tZone %4s, use %4g nodes of type %s\n" % (zone, instance.sol_N[node, zone], node))

    outfile.write("# List of activated channels:\n")
    for channel in instance.channels:
        if instance.sol_C[channel]:
            outfile.write("\tUse %4g channels of type %s\n" % (instance.sol_C[channel], channel))

    outfile.write("# Tasks allocation:\n")
    for zone in instance.zones:
        for task in instance.tasks:
            if task.zone == zone:
                for node in task.getAllowedNode():
                    for nodeIndex in Set_UB_on_N[node, zone]:
                        if instance.sol_w[task, node, nodeIndex]:
                            task.setDeployedIn(node, nodeIndex, zone)
                            outfile.write("\tTask %-24s inside node Zone%s.%s.%s\n" % (task, zone, node, nodeIndex))

    outfile.write("# Data-Flows allocation:\n")
    for dataflow in instance.dataflows:
        for channel in dataflow.getAllowedChannel():
            contiguity = instance.contiguities.get((dataflow.source.zone, dataflow.target.zone, channel))
            for channelIndex in Set_UB_on_C[channel]:
                if instance.sol_h[dataflow, channel, channelIndex]:
                    dataflow.setDeployedIn(channel, channelIndex)
                    outfile.write("\tDataflow %-24s inside channel %s.%s\n" % (dataflow, channel, channelIndex))

    # -----------------------------------------------------------------------------------------------------------------
    outfile.write("*                                  \n")
    outfile.write("* Final Statistics:                \n")
    outfile.write("* \tEconomic Cost      : %s      \n" % (total_cost_nodes + total_cost_wirls + total_cost_cable))
    outfile.write("* \t\tNodes Deployment     : %s\n" % total_cost_nodes)
    outfile.write("* \t\tWireless Channels    : %s\n" % total_cost_wirls)
    outfile.write("* \t\tCable    Channels    : %s\n" % total_cost_cable)
    outfile.write("* \tEnergy Consumption : %s      \n" % (total_energy_nodes +
                                                           total_energy_nodes_usage +
                                                           total_energy_channels +
                                                           total_energy_channels_usage))
    outfile.write("* \t\tNodes Power          : %s\n" % total_energy_nodes)
    outfile.write("* \t\tNodes Power Usage    : %s\n" % total_energy_nodes_usage)
    outfile.write("* \t\tChannels Power       : %s\n" % total_energy_channels)
    outfile.write("* \t\tChannels Power Usage : %s\n" % total_energy_channels_usage)
    outfile.write("* \tTotal Delay        : %s      \n" % (total_delay_wireless + total_delay_cable))
    outfile.write("* \t\tWireless Channels    : %s\n" % total_delay_wireless)
    outfile.write("* \t\tCable    Channels    : %s\n" % total_delay_cable)
    outfile.write("* \tTotal Error        : %s      \n" % (total_error_wireless + total_error_cable))
    outfile.write("* \t\tWireless Channels    : %s\n" % total_error_wireless)
    outfile.write("* \t\tCable    Channels    : %s\n" % total_error_cable)

    checker = NetworkChecker(instance.nodes,
                             instance.channels,
                             instance.zones,
                             instance.contiguities,
                             instance.tasks,
                             instance.dataflows,
                             instance.sol_N,
                             instance.sol_C,
                             instance.sol_w,
                             instance.sol_h,
                             Set_UB_on_C,
                             Set_UB_on_N,
                             outfile)
    if not checker.checkNetwork():
        outcome_txt = "FAILED"

elif m.status == GRB.Status.INF_OR_UNBD:
    outfile.write("Model is infeasible or unbounded\n")
    outcome_txt = "FAILED"
    m.computeIIS()
    m.write("model.ilp")
    QuitSynthesizer("FAILED")

elif m.status == GRB.Status.INFEASIBLE:
    outfile.write("Model is infeasible\n")
    outcome_txt = "FAILED"
    m.computeIIS()
    m.write("model.ilp")

elif m.status == GRB.Status.UNBOUNDED:
    outfile.write("Model is unbounded\n")
    outcome_txt = "FAILED"

else:
    outfile.write("Optimization ended with status %d\n" % m.status)
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
                                     instance.sol_N,
                                     instance.sol_C,
                                     instance.sol_w,
                                     instance.sol_h,
                                     Set_UB_on_C,
                                     Set_UB_on_N)
    umlPrinter.printNetwork()
    print("*##########################################")
    print("* Generating Technological Library...")
    techLibPrinter = TechLibPrinter(instance.nodes, instance.channels)
    techLibPrinter.printTechLib()

if SCNSL_GENERATION == 1:
    scnslPrinter = ScnslGenerator(instance.nodes, instance.channels, instance.zones, instance.contiguities,
                                  instance.tasks, instance.dataflows,
                                  instance.sol_N,
                                  instance.sol_C,
                                  instance.sol_w, instance.sol_h, Set_UB_on_C, Set_UB_on_N)
    scnslPrinter.printScnslNetwork("main.cc")

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

outfile.flush()
outfile.close()

QuitSynthesizer()

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

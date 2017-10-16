class NetworkChecker:
    def __init__(self,
                 NodeList,
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
                 indexSetOfClonesOfNodesInArea):
        self.NodeList = NodeList
        self.ChannelList = ChannelList
        self.ZoneList = ZoneList
        self.ContiguityList = ContiguityList
        self.TaskList = TaskList
        self.DataFlowList = DataFlowList
        self.SolN = SolN
        self.SolC = SolC
        self.SolW = SolW
        self.SolH = SolH
        self.indexSetOfClonesOfChannel = indexSetOfClonesOfChannel
        self.indexSetOfClonesOfNodesInArea = indexSetOfClonesOfNodesInArea
        print("# NetworkChecker instantiated...")

    def checkNetwork(self):
        print("#     1. Checking if all the tasks have been deployed...")
        for task in self.TaskList:
            taskPlaced = False
            for node in task.getAllowedNode():
                for nodeIndex in self.indexSetOfClonesOfNodesInArea[node, task.zone]:
                    if self.SolW[task, node, nodeIndex]:
                        if (taskPlaced):
                            print("[Error] Task %s has already been placed." % (task))
                            exit(1)
                        taskPlaced = True
            if (not taskPlaced):
                print("[Error] Task %s has not been placed." % (task))
                exit(1)

        print("#     2. Checking if all the dataflows have been deployed...")
        for dataflow in self.DataFlowList:
            dataflowPlaced = False
            SourceNode = dataflow.source.getDeployedIn()
            TargetNode = dataflow.target.getDeployedIn()
            for channel in dataflow.getAllowedChannel():
                for channelIndex in self.indexSetOfClonesOfChannel[channel]:
                    if self.SolH[dataflow, channel, channelIndex]:
                        if (SourceNode == TargetNode):
                            print(
                                "[Warning] Dataflow %s has been deployed inside channel (%s, %s), it was not necessary." % (
                                    dataflow, channel, channelIndex))
                        else:
                            if (dataflowPlaced):
                                print("[Error] Dataflow %s has already been placed." % (dataflow))
                                exit(1)
                            dataflowPlaced = True
            if (SourceNode != TargetNode):
                if (not dataflowPlaced):
                    print("[Error] Dataflow %s has not been placed." % (dataflow))
                    exit(1)

        print("#     3. Checking if the tasks deployment is compliant with the nodes sizes...")
        for zone in self.ZoneList:
            for node in self.NodeList:
                for nodeIndex in self.indexSetOfClonesOfNodesInArea[node, zone]:
                    OccupiedSpace = 0
                    for task in node.getAllowedTask():
                        if (task.zone == zone):
                            if self.SolW.get((task, node, nodeIndex), False):
                                OccupiedSpace += task.size
                    if (OccupiedSpace > node.size):
                        print("[Error] The space occupide inside node %s is over the limit." % (node))
                        exit(1)

        print(
            "#     4. Checking if cabled channels contain only dataflows which have tasks in the same pair of nodes...")
        for channel in self.ChannelList:
            if (not channel.wireless):
                for channelIndex in self.indexSetOfClonesOfChannel[channel]:
                    ConnectedNodes = set()
                    for dataflow in channel.getAllowedDataFlow():
                        if self.SolH[dataflow, channel, channelIndex]:
                            SourceNode = dataflow.source.getDeployedIn()
                            ConnectedNodes.add("%s_%s_%s" % (SourceNode[0], SourceNode[1], SourceNode[2]))
                            TargetNode = dataflow.target.getDeployedIn()
                            ConnectedNodes.add("%s_%s_%s" % (TargetNode[0], TargetNode[1], TargetNode[2]))
                    if (len(ConnectedNodes) > 2):
                        print("[Error] Cabled channel %s is connecting more than two nodes." % (channel))
                        exit(1)

        print("#     5. Checking if wireless channels has been placed between zones with zero contiguity...")
        for channel in self.ChannelList:
            if channel.wireless:
                for channelIndex in self.indexSetOfClonesOfChannel[channel]:
                    connecting_tasks = []
                    for dataflow in channel.getAllowedDataFlow():
                        if self.SolH[dataflow, channel, channelIndex]:
                            connecting_tasks.append(dataflow.source)
                            connecting_tasks.append(dataflow.target)
                            contiguity = self.ContiguityList.get((dataflow.source.zone, dataflow.target.zone, channel))
                            if contiguity.conductance <= 0:
                                print "[Error] The %s-th wireless channel %s contains a " % (channelIndex, channel)
                                print "dataflow connecting tasks inside two zones with zero conductance."
                    for task1 in connecting_tasks:
                        for task2 in connecting_tasks:
                            if task1 < task2:
                                contiguity = self.ContiguityList.get((task1.zone, task2.zone, channel))
                                if contiguity.conductance <= 0:
                                    output = "[Error] Channel %s-%s contiguity %s" \
                                             % (channel, channelIndex, contiguity)
                                    print output
                    del connecting_tasks

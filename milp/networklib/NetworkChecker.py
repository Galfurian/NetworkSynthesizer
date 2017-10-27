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
                 indexSetOfClonesOfNodesInArea,
                 outfile):
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
        self.outfile = outfile
        self.outfile.write("* NetworkChecker instantiated...\n")

    def checkNetwork(self):
        # -------------------------------------------------------------------------------------------------------------
        self.outfile.write("*     - Checking if all the tasks have been deployed once...\n")
        for task in self.TaskList:
            task_placed = False
            for node in task.getAllowedNode():
                for nodeIndex in self.indexSetOfClonesOfNodesInArea[node, task.zone]:
                    if self.SolW[task, node, nodeIndex]:
                        if task_placed:
                            self.outfile.write("[Error] Task %s has already been placed.\n" % (task))
                            return False
                        task_placed = True
            if not task_placed:
                self.outfile.write("[Error] Task %s has not been placed.\n" % (task))
                return False

        # -------------------------------------------------------------------------------------------------------------
        self.outfile.write("*     - Checking if all the dataflows have been deployed...\n")
        for dataflow in self.DataFlowList:
            dataflow_placed = False
            source_node = dataflow.source.getDeployedIn()
            target_node = dataflow.target.getDeployedIn()
            for channel in dataflow.getAllowedChannel():
                for channelIndex in self.indexSetOfClonesOfChannel[channel]:
                    if self.SolH[dataflow, channel, channelIndex]:
                        if source_node == target_node:
                            self.outfile.write(
                                "* [Warning] Unnecessary deployment of %s, inside the channel (%s, %s),\n"
                                % (dataflow, channel, channelIndex))
                            self.outfile.write("*           in fact source and target are in %s and %s respectively.\n"
                                               % (source_node, target_node))
                        else:
                            if dataflow_placed:
                                self.outfile.write("[Error] Dataflow %s has already been placed.\n" % (dataflow))
                                return False
                            dataflow_placed = True
            if (source_node != target_node) and not dataflow_placed:
                self.outfile.write("[Error] Dataflow %s has not been placed.\n" % (dataflow))
                return False

        # -------------------------------------------------------------------------------------------------------------
        self.outfile.write("*     - Checking if the tasks deployment is compliant with the nodes sizes...\n")
        for zone in self.ZoneList:
            for node in self.NodeList:
                for nodeIndex in self.indexSetOfClonesOfNodesInArea[node, zone]:
                    occupied_space = 0
                    for task in node.getAllowedTask():
                        if task.zone == zone:
                            if self.SolW.get((task, node, nodeIndex), False):
                                occupied_space += task.size
                    if occupied_space > node.size:
                        self.outfile.write("[Error] The space occupied inside node %s is over the limit.\n" % (node))
                        return False

        # -------------------------------------------------------------------------------------------------------------
        self.outfile.write(
            "*     - Checking if cabled channels contain only dataflows which have tasks in the same pair of nodes...\n")
        for channel in self.ChannelList:
            if (not channel.wireless):
                for channelIndex in self.indexSetOfClonesOfChannel[channel]:
                    ConnectedNodes = set()
                    for dataflow in channel.getAllowedDataFlow():
                        if self.SolH[dataflow, channel, channelIndex]:
                            source_node = dataflow.source.getDeployedIn()
                            ConnectedNodes.add("%s_%s_%s" % (source_node[0], source_node[1], source_node[2]))
                            target_node = dataflow.target.getDeployedIn()
                            ConnectedNodes.add("%s_%s_%s" % (target_node[0], target_node[1], target_node[2]))
                    if (len(ConnectedNodes) > 2):
                        self.outfile.write("[Error] Cabled channel %s is connecting more than two nodes.\n" % (channel))
                        return False

        # -------------------------------------------------------------------------------------------------------------
        self.outfile.write("*     - Checking if a wired channel contains a dataflow with mobile tasks...\n")
        for channel in self.ChannelList:
            if not channel.wireless:
                for channelIndex in self.indexSetOfClonesOfChannel[channel]:
                    for dataflow in channel.getAllowedDataFlow():
                        if self.SolH[dataflow, channel, channelIndex]:
                            source_node = dataflow.source.getDeployedIn()
                            if source_node[0].mobile:
                                self.outfile.write("[Error] Wired channel %s used with mobile dataflow %s [ND:%s].\n"
                                                   % (channel, dataflow, source_node))
                                return False
                            target_node = dataflow.target.getDeployedIn()
                            if target_node[0].mobile:
                                self.outfile.write("[Error] Wired channel %s used with mobile dataflow %s [ND:%s].\n"
                                                   % (channel, dataflow, target_node))
                                return False

        # -------------------------------------------------------------------------------------------------------------
        self.outfile.write(
            "*     - Checking if wireless channels has been placed between zones with zero contiguity...\n")
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
                                self.outfile.write(
                                    "[Error] The %s-th wireless channel %s contains a \n" % (channelIndex, channel))
                                self.outfile.write(
                                    "dataflow connecting tasks inside two zones with zero conductance.\n")
                                return False
                    for task1 in connecting_tasks:
                        for task2 in connecting_tasks:
                            if task1 < task2:
                                contiguity = self.ContiguityList.get((task1.zone, task2.zone, channel))
                                if contiguity.conductance <= 0:
                                    output = "[Error] Channel %s-%s contiguity %s\n" \
                                             % (channel, channelIndex, contiguity)
                                    self.outfile.write("%s.\n" % output)
                                    return False
                    del connecting_tasks

        # -------------------------------------------------------------------------------------------------------------
        self.outfile.write("*     - Checking if a non-mobile node is hosting a mobile task...\n")
        for task in self.TaskList:
            for node in task.getAllowedNode():
                for nodeIndex in self.indexSetOfClonesOfNodesInArea[node, task.zone]:
                    if self.SolW[task, node, nodeIndex] and task.mobile and not node.mobile:
                        self.outfile.write(
                            "[Error] Mobile task %s is hosted inside the non-mobile node %s.\n" % (task, node))
                        return False

        # -------------------------------------------------------------------------------------------------------------
        # self.outfile.write("*     - Checking compliance with maximum connections of channels...\n")
        # for channel in self.ChannelList:
        #     for channelIndex in self.indexSetOfClonesOfChannel[channel]:
        #         ConnectedNodes = set()
        #         for dataflow in channel.getAllowedDataFlow():
        #             if self.SolH[dataflow, channel, channelIndex]:
        #                 source_node = dataflow.source.getDeployedIn()
        #                 ConnectedNodes.add("%s_%s_%s" % (source_node[0], source_node[1], source_node[2]))
        #                 target_node = dataflow.target.getDeployedIn()
        #                 ConnectedNodes.add("%s_%s_%s" % (target_node[0], target_node[1], target_node[2]))
        #         if (len(ConnectedNodes) > channel.max_conn):
        #             self.outfile.write("[Error] Cabled channel %s.%s is connecting to much nodes (MAX:%s).\n"
        #                                % (channel, channelIndex, channel.max_conn))
        #             return False
        return True

class ScnslGenerator:
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
        print("# Scnsl Generator instantiated...")

    def printScnslNetwork(self, outputFile):
        print("#     1. Writing the final code inside '%s'..."%(outputFile))
        outFile = open(outputFile, 'w')

        print("#     2. Retrieving an instance of Scnsl.")
        outFile.write("Scnsl::Setup::Scnsl_t * scnsl = Scnsl::Setup::Scnsl_t::get_instance();\n")

        print("#     3. Generating the channels catalog.")
        outFile.write("// ///////////////////////  CHANNEL CATALOG  /////////////////////////////\n")
        for channel in self.ChannelList:
            outFile.write(channel.toScnsl()+"\n")
            outFile.write("\n")
        TotalConnectedNodes = {}
        for channel in self.ChannelList:
            for channelIndex in self.indexSetOfClonesOfChannel[channel]:
                ConnectedNodes = {}
                NumConnectedNodes = 0
                for dataflow in channel.getAllowedDataFlow():
                    if self.SolH[dataflow, channel, channelIndex]:
                        SourceNode = dataflow.source.getDeployedIn()
                        TargetNode = dataflow.target.getDeployedIn()
                        SourceNodeName = ("n_%s_%s_%s"%(SourceNode[0], SourceNode[1], dataflow.source.zone))
                        TargetNodeName = ("n_%s_%s_%s"%(TargetNode[0], TargetNode[1], dataflow.target.zone))

                        if(ConnectedNodes.get(SourceNodeName, -1) == -1):
                            ConnectedNodes[SourceNodeName] = 1
                        else:
                            ConnectedNodes[SourceNodeName] += 1
                        if(ConnectedNodes.get(TargetNodeName, -1) == -1):
                            ConnectedNodes[TargetNodeName] = 1
                        else:
                            ConnectedNodes[TargetNodeName] += 1
                        NumConnectedNodes += 2
                if(len(ConnectedNodes) > 0):
                    ChannelName    = ("ch_%s_%s"%(channel.id, channelIndex))
                    TotalConnectedNodes[ChannelName] = NumConnectedNodes
        outFile.write("// ///////////////////////  END CHANNEL CATALOG  /////////////////////////\n")

        print("#     4. Deploying nodes.")
        outFile.write("// //////////////////////////  NODE CREATION  ////////////////////////////\n")
        alreadyDefinedNode = {}
        for zone in self.ZoneList:
            for task in self.TaskList:
                if(task.zone == zone):
                    for node in task.getAllowedNode():
                        for nodeIndex in self.indexSetOfClonesOfNodesInArea[node, zone]:
                            if self.SolW[task, node, nodeIndex]:
                                if(alreadyDefinedNode.get((node, nodeIndex, zone), -1) == -1):
                                    alreadyDefinedNode[node, nodeIndex, zone] = 1
                                    outFile.write('Scnsl::Core::Node_t * n_%s_%s_%s = scnsl->createNode();\n'%(node, nodeIndex, zone))
        outFile.write("// ////////////////////////  END NODE CREATION  //////////////////////////\n")

        print("#     5. Deploying channels.")
        outFile.write("// //////////////////////////  CHANNEL SETUP  ////////////////////////////\n")
        for channel in self.ChannelList:
            for channelIndex in self.indexSetOfClonesOfChannel[channel]:
                ChannelName    = ("ch_%s_%s"%(channel.id, channelIndex))
                if(TotalConnectedNodes.get(ChannelName, -1) > 0):
                    csb     = ("csb_%s"%(channel.id))
                    csbName = ("csb_%s_%s"%(channel.id, channelIndex))
                    outFile.write('%s.name         = \"%s\";\n'%(csb, csbName))
                    outFile.write('%s.nodes_number = %s;\n'%(csb, TotalConnectedNodes[ChannelName]))
                    TotalConnectedNodes[ChannelName]
                    outFile.write('Scnsl::Core::Channel_if_t * %s = scnsl->createChannel(%s);\n'%(ChannelName, csb))
        outFile.write("// ////////////////////////  END CHANNEL SETUP  //////////////////////////\n")

        TaskTraffic = {}
        ProxyNumber = {}
        for dataflow in self.DataFlowList:
            SourceNode = dataflow.source.getDeployedIn()
            TargetNode = dataflow.target.getDeployedIn()
            if(ProxyNumber.get(dataflow.source, -1) == -1):
                ProxyNumber[dataflow.source] = 1;
            else:
                ProxyNumber[dataflow.source] += 1;
            if(SourceNode != TargetNode):
                if(ProxyNumber.get(dataflow.target, -1) == -1):
                    ProxyNumber[dataflow.target] = 1;
                else:
                    ProxyNumber[dataflow.target] += 1;
            if(TaskTraffic.get(dataflow.source, -1) == -1):
                TaskTraffic[dataflow.source] = dataflow.size;
            else:
                TaskTraffic[dataflow.source] +=  dataflow.size;

        print("#     6. Instantiating the list of tasks.");
        outFile.write("// ////////////////////////////  TASK SETUP  /////////////////////////////\n")
        incrementalId = 1;
        for zone in self.ZoneList:
            for task in self.TaskList:
                if(task.zone == zone):
                    for node in task.getAllowedNode():
                        for nodeIndex in self.indexSetOfClonesOfNodesInArea[node, zone]:
                            if self.SolW[task, node, nodeIndex]:
                                if(ProxyNumber.get(task, -1) > 0):
                                    NodeName = ("n_%s_%s_%s"%(node, nodeIndex, zone))
                                    outFile.write("Sensor %s(\"%s\", %s, %s, %s, %s);\n"%(task.label, task.label, incrementalId, NodeName, ProxyNumber[task], TaskTraffic.get(task,0)));
                                    incrementalId += 1;
        outFile.write("// ////////////////////////// END TASK SETUP /////////////////////////////\n")

        print("#     7. Generating node binding.");
        outFile.write("// //////////////////////////  BINDING SETUP  ////////////////////////////\n")
        alreadyDefinedBSB = {}
        AlreadyBoundTask = {}
        for channel in self.ChannelList:
            for channelIndex in self.indexSetOfClonesOfChannel[channel]:
                for dataflow in channel.getAllowedDataFlow():
                    if self.SolH[dataflow, channel, channelIndex]:
                        ChannelName    = ("ch_%s_%s"%(channel.id, channelIndex))

                        SourceNode = dataflow.source.getDeployedIn()
                        SourceNodeName = ("n_%s_%s_%s"%(SourceNode[0], SourceNode[1], dataflow.source.zone))

                        TargetNode = dataflow.target.getDeployedIn()
                        TargetNodeName = ("n_%s_%s_%s"%(TargetNode[0], TargetNode[1], dataflow.target.zone))

                        bsbSourceName = ("bsb_%s_%s_%s_%s"%(SourceNode[0], SourceNode[1], channel.id, channelIndex))
                        counter = 1;
                        while(alreadyDefinedBSB.get(bsbSourceName, -1) != -1):
                            bsbSourceName = ("%s_%s"%(bsbSourceName, counter))
                        alreadyDefinedBSB[bsbSourceName] = 1
                        outFile.write("Scnsl::Setup::BindSetup_base_t %s;\n"%(bsbSourceName))
                        outFile.write("%s.extensionId = \"core\";\n"%(bsbSourceName))
                        outFile.write("%s.destinationNode = %s;\n"%(bsbSourceName, TargetNodeName))
                        outFile.write("%s.node_binding.x = 0;\n"%(bsbSourceName))
                        outFile.write("%s.node_binding.y = 0;\n"%(bsbSourceName))
                        outFile.write("%s.node_binding.z = 0;\n"%(bsbSourceName))
                        outFile.write("%s.node_binding.bitrate = Scnsl::Protocols::Mac_802_15_4::BITRATE;\n"%(bsbSourceName))
                        outFile.write("%s.node_binding.transmission_power = 100;\n"%(bsbSourceName))
                        outFile.write("%s.node_binding.receiving_threshold = 10;\n"%(bsbSourceName))
                        outFile.write("\n")
                        outFile.write("scnsl->bind(%s, %s, %s);\n"%(SourceNodeName, ChannelName, bsbSourceName));
                        outFile.write("scnsl->bind(&%s, &%s, %s, %s, NULL);\n"%(dataflow.source, dataflow.target, ChannelName, bsbSourceName))
                        outFile.write("\n")

                        bsbTargetName = ("bsb_%s_%s_%s_%s"%(TargetNode[0], TargetNode[1], channel.id, channelIndex))

                        counter = 1;
                        while(alreadyDefinedBSB.get(bsbTargetName, -1) != -1):
                            bsbTargetName = ("%s_%s"%(bsbTargetName, counter))
                        alreadyDefinedBSB[bsbTargetName] = 1
                        #if(alreadyDefinedBSB.get((bsbTargetName,ChannelName), -1) == -1):
                        #    alreadyDefinedBSB[bsbTargetName, ChannelName] = 1
                        outFile.write("Scnsl::Setup::BindSetup_base_t %s;\n"%(bsbTargetName))
                        outFile.write("%s.extensionId = \"core\";\n"%(bsbTargetName))
                        outFile.write("%s.destinationNode = %s;\n"%(bsbTargetName, SourceNodeName))
                        outFile.write("%s.node_binding.x = 0;\n"%(bsbTargetName))
                        outFile.write("%s.node_binding.y = 0;\n"%(bsbTargetName))
                        outFile.write("%s.node_binding.z = 0;\n"%(bsbTargetName))
                        outFile.write("%s.node_binding.bitrate = Scnsl::Protocols::Mac_802_15_4::BITRATE;\n"%(bsbTargetName))
                        outFile.write("%s.node_binding.transmission_power = 100;\n"%(bsbTargetName))
                        outFile.write("%s.node_binding.receiving_threshold = 10;\n"%(bsbTargetName))
                        outFile.write("\n")
                        outFile.write("scnsl->bind(%s, %s, %s);\n"%(TargetNodeName, ChannelName, bsbTargetName));
                        outFile.write("scnsl->bind(&%s, &%s, %s, %s, NULL);\n"%(dataflow.target, dataflow.source,ChannelName, bsbTargetName))
                        outFile.write("\n")
        outFile.write("// ////////////////////////  END BINDING SETUP  //////////////////////////\n")
        print("# Done");

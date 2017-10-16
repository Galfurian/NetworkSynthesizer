from lxml import etree
from lxml.builder import ElementMaker
from xml.dom import minidom

class UmlGenerator:
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
        print("# Generator instantiated...")

    def printNetwork(self):
        xsi = "http://www.w3.org/2001/XMLSchema-instance"
        xmi = "http://schema.omg.org/spec/XMI/2.1"
        uml = "http://www.eclipse.org/uml2/3.0.0/UML"
        Resources="http://Resources/N2XwPJDEeS1NtI8921z6A"
        rootNs = {"xsi": xsi, "xmi": xmi, "uml": uml, "Resources": Resources}
        root  = etree.Element("{" + xmi + "}XMI", nsmap=rootNs)

        # Add the Network Model.
        model = etree.Element("{" + uml + "}Model")
        root.append(model)

        deployedContiguities = {}
        deployedZones        = {}
        deployedNodes        = {}
        deployedChannels     = {}

        # Add the Network Components.
        for dataflow in self.DataFlowList:
            dfNode = etree.Element("{" + Resources + "}DataFlow")
            dfNode.set("{"+xmi+"}id",     "%s"%(dataflow))
            dfNode.set("base_Dependency", "%s"%(dataflow))
            dfNode.set("bindID",          "%s_bind_id"%(dataflow))
            dfNode.set("throughput",      "%s"%(dataflow.bandwidth))
            dfNode.set("max_delay",       "%s"%(dataflow.max_delay))
            dfNode.set("max_error_rate",  "%s"%(dataflow.max_error))
            root.append(dfNode)

        for channel in self.ChannelList:
            for p in self.indexSetOfClonesOfChannel[channel]:
                used   = False
                dfList = ""
                for dataflow in self.DataFlowList:
                    if self.SolH[dataflow, channel, p]:
                        if(used == False):
                            dfList  = "%s"%(dataflow);
                        else:
                            dfList += " %s"%(dataflow);
                        used = True
                if(used):
                    chNode = etree.Element("{" + Resources + "}AbstractChannel")
                    chNode.set("{"+xmi+"}id",     "Channel_%s_%s"%(channel, p))
                    chNode.set("base_Classifier", "Channel_%s_%s"%(channel, p))
                    chNode.set("transmMode",      "fullDuplex")
                    chNode.set("dataFlow",        "%s"%(dfList))
                    chNode.set("cost",            "%s"%(channel.cost))
                    chNode.set("power",           "%s"%(channel.power))
                    chNode.set("max_throughput",  "%s"%(channel.bandwidth))
                    chNode.set("delay",           "%s"%(channel.delay))
                    chNode.set("error_rate",      "%s"%(channel.error))
                    if(channel.wireless):
                        chNode.set("base_Device", "Channel_%s_%s"%(channel, p))
                    else:
                        chNode.set("base_CommunicationPath", "Channel_%s_%s"%(channel, p))
                    root.append(chNode)

        for contiguity in self.ContiguityList:
            if(deployedContiguities.get((contiguity[0], contiguity[1]), -1) == -1):
                deployedContiguities[contiguity[0], contiguity[1]] = 1
                contNode = etree.Element("{" + Resources + "}Contiguity")
                contNode.set("{"+xmi+"}id",     "Contiguity_%s_%s"%(contiguity[0], contiguity[1]))
                contNode.set("base_Dependency", "Contiguity_%s_%s"%(contiguity[0], contiguity[1]))
                root.append(contNode)

        for task in self.TaskList:
            tskNode = etree.Element("{" + Resources + "}Task")
            tskNode.set("{"+xmi+"}id",   "%s"%(task))
            tskNode.set("base_Artifact", "%s"%(task))
            tskNode.set("behavior",      "%s_behavior"%(task))
            tskNode.set("cpu_usage",     "%s"%(task.size))
            tskNode.set("memory_usage",  "%s"%(task.size))
            if(task.mobile):
                tskNode.set("requiresMobility", "true")
            root.append(tskNode)

        alreadyDefinedNode = {}
        for zone in self.ZoneList:
            for task in self.TaskList:
                if(task.zone == zone):
                    for node in self.NodeList:
                        if(node.isGoodFor(task)):
                            for nodeIndex in self.indexSetOfClonesOfNodesInArea[node, zone]:
                                if self.SolW[task, node, nodeIndex]:
                                    if(alreadyDefinedNode.get((node, nodeIndex, zone), -1) == -1):
                                        alreadyDefinedNode[node, nodeIndex, zone] = 1
                                        ndNode = etree.Element("{" + Resources + "}Node")
                                        ndNode.set("{"+xmi+"}id",     "Node_%s_%s_Zone_%s"%(node, nodeIndex, zone))
                                        ndNode.set("base_Classifier", "Node_%s_%s_Zone_%s"%(node, nodeIndex, zone))
                                        ndNode.set("base_Node",       "Node_%s_%s_Zone_%s"%(node, nodeIndex, zone))
                                        ndNode.set("cpu",             "%s"%(node.size))
                                        ndNode.set("memory",          "%s"%(node.size))
                                        ndNode.set("cost",            "%s"%(node.cost))
                                        ndNode.set("power",           "%s"%(node.power))
                                        if(node.mobile):
                                            ndNode.set("mobility",    "true")
                                        root.append(ndNode)

        for zone in self.ZoneList:
            znNode = etree.Element("{" + Resources + "}Zone")
            znNode.set("{"+xmi+"}id",  "Zone_%s"%(zone))
            znNode.set("base_Package", "Zone_%s"%(zone))
            znNode.set("position",     "(%s,%s,%s)"%(zone.x,zone.y,zone.z))
            root.append(znNode)


        # Define the Network name.
        model.set("{"+xmi+"}id", "Unknown")
        model.set("name", "Unknown")

        for task in self.TaskList:
            tskPeNode = etree.Element("packagedElement")
            tskPeNode.set("{"+xmi+"}type",    "uml:Artifact")
            tskPeNode.set("{"+xmi+"}id",      "%s"%(task))
            tskPeNode.set("name",             "%s"%(task))
            model.append(tskPeNode)

        for dataflow in self.DataFlowList:
            dfPeNode = etree.Element("packagedElement")
            dfPeNode.set("{"+xmi+"}type", "uml:Dependency")
            dfPeNode.set("{"+xmi+"}id",   "%s"%(dataflow))
            dfPeNode.set("name",          "%s"%(dataflow))
            dfPeNode.set("supplier",      "%s"%(dataflow.source))
            dfPeNode.set("client",        "%s"%(dataflow.target))
            model.append(dfPeNode)

        for contiguity in deployedContiguities:
            cntPeNode = etree.Element("packagedElement")
            cntPeNode.set("{"+xmi+"}type", "uml:Dependency")
            cntPeNode.set("{"+xmi+"}id",   "Contiguity_%s_%s"%(contiguity[0], contiguity[1]))
            cntPeNode.set("name",          "Contiguity_%s_%s"%(contiguity[0], contiguity[1]))
            cntPeNode.set("supplier",      "Zone_%s"%(contiguity[0]))
            cntPeNode.set("client",        "Zone_%s"%(contiguity[1]))
            model.append(cntPeNode)

        taskDeplymentCounter = 0

        for zone in self.ZoneList:
            znPeNode = etree.Element("packagedElement")
            znPeNode.set("{"+xmi+"}type",    "uml:Package")
            znPeNode.set("{"+xmi+"}id",      "Zone_%s"%(zone))
            znPeNode.set("name",             "Zone_%s"%(zone))
            model.append(znPeNode)
            deployedZones["Zone_%s"%(zone)] = znPeNode

        for zone in self.ZoneList:
            znPeNode = deployedZones.get("Zone_%s"%(zone))

            for zone2 in self.ZoneList:
                if(deployedContiguities.get((zone, zone2), -1) == 1):
                    znPeNode.set("clientDependency", "Contiguity_%s_%s"%(zone, zone2))
                if(deployedContiguities.get((zone2, zone), -1) == 1):
                    znPeNode.set("clientDependency", "Contiguity_%s_%s"%(zone2, zone))

            for node in self.NodeList:
                for nodeIndex in self.indexSetOfClonesOfNodesInArea[node, zone]:
                    used = False
                    tskList = ""
                    for task in self.TaskList:
                        if(task.zone == zone):
                            if self.SolW[task, node, nodeIndex]:
                                if(used == False):
                                    tskList  = "%s"%(task);
                                else:
                                    tskList += " %s"%(task);
                                used = True
                    if(used):
                        ndPeNode = etree.Element("packagedElement")
                        deplNode = etree.Element("deployment")
                        deplNode.set("{"+xmi+"}id",      "Deployment_Artifacts_%s"%(taskDeplymentCounter))
                        deplNode.set("name",             "Deployment_Artifacts_%s"%(taskDeplymentCounter))
                        deplNode.set("supplier",         "%s"%(tskList))
                        deplNode.set("client",           "Node_%s_%s_Zone_%s"%(node, nodeIndex, zone))
                        deplNode.set("deployedArtifact", "%s"%(tskList))
                        ndPeNode.append(deplNode)
                        ndPeNode.set("{"+xmi+"}type",    "uml:Node")
                        ndPeNode.set("{"+xmi+"}id",      "Node_%s_%s_Zone_%s"%(node, nodeIndex, zone))
                        ndPeNode.set("name",             "Node_%s_%s_Zone_%s"%(node, nodeIndex, zone))
                        ndPeNode.set("clientDependency", "%s"%(deplNode.get("name")))
                        znPeNode.append(ndPeNode)
                        deployedNodes["Node_%s_%s_Zone_%s"%(node, nodeIndex, zone)] = ndPeNode
                        # Increment the counter for the deployment instances of the tasks.
                        taskDeplymentCounter += 1

        for channel in self.ChannelList:
            if (channel.wireless == 0):
                for channelIndex in self.indexSetOfClonesOfChannel[channel]:
                    for dataflow in self.DataFlowList:
                        if self.SolH[dataflow, channel, channelIndex]:
                            # Create the Channel Node.
                            chPeNode  = etree.Element("packagedElement")
                            model.append(chPeNode)

                            # Create the source end.
                            sourceEnd = etree.Element("ownedEnd")
                            chPeNode.append(sourceEnd)

                            # Create the target end.
                            targetEnd = etree.Element("ownedEnd")
                            chPeNode.append(targetEnd)

                            done       = False
                            for node in self.NodeList:
                                if(done != True):
                                    for nodeIndex in self.indexSetOfClonesOfNodesInArea[node, dataflow.source.zone]:
                                        if(done != True):
                                            if self.SolW[dataflow.source, node, nodeIndex]:
                                                sourceEnd.set("{"+xmi+"}id", "Channel_%s_%s_Node_%s_%s_Zone_%s"%(channel, channelIndex, node, nodeIndex, dataflow.source.zone))
                                                sourceEnd.set("name",        "Node_%s_%s_Zone_%s"%(node, nodeIndex, dataflow.source.zone))
                                                sourceEnd.set("type",        "Node_%s_%s_Zone_%s"%(node, nodeIndex, dataflow.source.zone))
                                                sourceEnd.set("isUnique",    "false")
                                                sourceEnd.set("association", "Channel_%s_%s"%(channel, channelIndex))
                                                # Set the termination.
                                                done = True
                            done = False
                            for node in self.NodeList:
                                if(done != True):
                                    for nodeIndex in self.indexSetOfClonesOfNodesInArea[node, dataflow.target.zone]:
                                        if(done != True):
                                            if self.SolW[dataflow.target, node, nodeIndex]:
                                                targetEnd.set("{"+xmi+"}id", "Channel_%s_%s_Node_%s_%s_Zone_%s"%(channel, channelIndex, node, nodeIndex, dataflow.target.zone))
                                                targetEnd.set("name",        "Node_%s_%s_Zone_%s"%(node, nodeIndex, dataflow.target.zone))
                                                targetEnd.set("type",        "Node_%s_%s_Zone_%s"%(node, nodeIndex, dataflow.target.zone))
                                                targetEnd.set("isUnique",    "false")
                                                targetEnd.set("association", "Channel_%s_%s"%(channel, channelIndex))
                                                # Set the termination.
                                                done = True
                            chPeNode.set("{"+xmi+"}type",    "uml:CommunicationPath")
                            chPeNode.set("{"+xmi+"}id",      "Channel_%s_%s"%(channel, channelIndex))
                            chPeNode.set("name",             "Channel_%s_%s"%(channel, channelIndex))
                            chPeNode.set("memberEnd",        "Channel_%s_%s_%s Channel_%s_%s_%s"%(channel, channelIndex, sourceEnd.get("name"), channel, channelIndex, targetEnd.get("name")))


        for channel in self.ChannelList:
            if (channel.wireless == 1):
                for channelIndex in self.indexSetOfClonesOfChannel[channel]:
                    for dataflow in self.DataFlowList:
                        if self.SolH[dataflow, channel, channelIndex]:
                            if(deployedChannels.get("Channel_%s_%s"%(channel, channelIndex)) is None):
                                chPeNode = etree.Element("packagedElement")
                                chPeNode.set("{"+xmi+"}type", "uml:Device")
                                chPeNode.set("{"+xmi+"}id",   "Channel_%s_%s"%(channel, channelIndex))
                                chPeNode.set("name",          "Channel_%s_%s"%(channel, channelIndex))
                                # Add the channel to the model.
                                model.append(chPeNode)
                                # Add the channel to the list of deployed channels.
                                deployedChannels["Channel_%s_%s"%(channel, channelIndex)] = chPeNode

        for channel in self.ChannelList:
            if (channel.wireless == 0):
                for channelIndex in self.indexSetOfClonesOfChannel[channel]:
                    for dataflow in self.DataFlowList:
                        if self.SolH[dataflow, channel, channelIndex]:
                            chPeNode = deployedChannels.get("Channel_%s_%s"%(channel, channelIndex))
                            done = False
                            for node in self.NodeList:
                                if(done != True):
                                    for nodeIndex in self.indexSetOfClonesOfNodesInArea[node, dataflow.source.zone]:
                                        if(done != True):
                                            if self.SolW[dataflow.source, node, nodeIndex]:
                                                ndChDepPeNode = etree.Element("packagedElement")
                                                ndChDepPeNode.set("{"+xmi+"}type", "uml:Dependency")
                                                ndChDepPeNode.set("{"+xmi+"}id",   "From_Node_%s_%s_Zone_%s_Channel_%s_%s"%(node, nodeIndex, dataflow.source.zone, channel, channelIndex))
                                                ndChDepPeNode.set("name",          "From_Node_%s_%s_Zone_%s_Channel_%s_%s"%(node, nodeIndex, dataflow.source.zone, channel, channelIndex))
                                                ndChDepPeNode.set("client",        "Node_%s_%s_Zone_%s"%(node, nodeIndex, dataflow.source.zone))
                                                ndChDepPeNode.set("supplier",      "Channel_%s_%s"%(channel, channelIndex))
                                                deployedNode = deployedNodes.get("Node_%s_%s_Zone_%s"%(node, nodeIndex, dataflow.source.zone), -1)
                                                if(deployedNode != -1):
                                                    deployedNode.set("clientDependency", "%s %s"%(deployedNode.get("clientDependency"), ndChDepPeNode.get("name")))
                                                # Set the termination.
                                                done = True
                                                model.append(ndChDepPeNode)
        printedTree = minidom.parseString(etree.tostring(root, encoding='unicode'))
        xmlFile = open('./TestCase.uml', 'w+')
        xmlFile.write(printedTree.toprettyxml(indent='    '))

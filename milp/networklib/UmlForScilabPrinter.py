from lxml import etree
from lxml.builder import ElementMaker
from xml.dom import minidom

class UmlForScilabPrinter:
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
        print("# UmlForScilabPrinter instantiated...")

    def printNetwork(self):
        ElementRoot = etree.Element("NETWORK")
        ElementTasks = etree.Element("TASKS")
        ElementDataFlows = etree.Element("DATAFLOWS")
        ElementNodes = etree.Element("NODES")
        ElementChannels = etree.Element("ABSTRACTCHANNELS")
        ElementZones = etree.Element("ZONES")
        ElementContiguities = etree.Element("CONTIGUITIES")

        ElementRoot.append(ElementTasks)
        ElementRoot.append(ElementDataFlows)
        ElementRoot.append(ElementNodes)
        ElementRoot.append(ElementChannels)
        ElementRoot.append(ElementZones)
        ElementRoot.append(ElementContiguities)

        for task in self.TaskList:
            ElementTask = etree.Element("TASK")
            ElementTask.set("name",task.label)
            ElementTask.set("m","%s"%(task.mobile))

            ElementCapacity = etree.Element("CAPACITY")
            ElementCapacity.set("name", "cpu_usage")
            ElementCapacity.set("value","%s"%(task.size))
            ElementTask.append(ElementCapacity)

            ElementCapacity = etree.Element("CAPACITY")
            ElementCapacity.set("name","memory_usage")
            ElementCapacity.set("value","%s"%(task.size))
            ElementTask.append(ElementCapacity)

            ElementTasks.append(ElementTask)

        for dataflow in self.DataFlowList:
            ElementDataFlow = etree.Element("DATAFLOW")
            ElementDataFlow.set("name","%s"%(dataflow.label))

            ElementTS = etree.Element("TS")
            ElementTS.set("name", dataflow.source.label)
            ElementDataFlow.append(ElementTS)

            ElementTD = etree.Element("TD")
            ElementTD.set("name", dataflow.target.label)
            ElementDataFlow.append(ElementTD)

            ElementCapacity = etree.Element("CAPACITY")
            ElementCapacity.set("max_delay",      "%s"%(dataflow.max_delay))
            ElementCapacity.set("max_error_rate", "%s"%(dataflow.max_error))
            ElementCapacity.set("max_throughput", "%s"%(dataflow.bandwidth))
            ElementDataFlow.append(ElementCapacity)

            ElementDataFlows.append(ElementDataFlow)

        for zone in self.ZoneList:
            for node in self.NodeList:
                for nodeIndex in self.indexSetOfClonesOfNodesInArea[node, zone]:
                    PlacedTasks = []
                    for task in node.getAllowedTask():
                        if(task.zone == zone):
                            if self.SolW.get((task, node, nodeIndex), False):
                                PlacedTasks.append(task)
                    if(len(PlacedTasks) > 0):
                        ElementNode = etree.Element("NODE")
                        ElementNode.set("name", "%s_%s_%s"%(node.label, nodeIndex, zone.label))
                        ElementNode.set("k",    "%s"%(node.cost))
                        ElementNode.set("p",    "%s"%(node.power))
                        ElementNodeTasks = etree.Element("T")
                        for placedTask in PlacedTasks:
                            ElementNodeTask = etree.Element("TASK")
                            ElementNodeTask.set("name", "%s"%(placedTask.label))
                            ElementNodeTasks.append(ElementNodeTask)
                        ElementNode.append(ElementNodeTasks)

                        ElementCapacity = etree.Element("CAPACITY")
                        ElementCapacity.set("name", "cpu")
                        ElementCapacity.set("gamma", "0")
                        ElementCapacity.set("value","%s"%(node.size))
                        ElementNode.append(ElementCapacity)

                        ElementCapacity = etree.Element("CAPACITY")
                        ElementCapacity.set("name","memory")
                        ElementCapacity.set("gamma", "0")
                        ElementCapacity.set("value","%s"%(node.size))
                        ElementNode.append(ElementCapacity)

                        ElementNodes.append(ElementNode)

        for channel in self.ChannelList:
            for channelIndex in self.indexSetOfClonesOfChannel[channel]:
                PlacedDataFlows = []
                for dataflow in channel.getAllowedDataFlow():
                    if self.SolH.get((dataflow, channel, channelIndex), False):
                        PlacedDataFlows.append(dataflow)
                if(len(PlacedDataFlows) > 0):
                    ElementChannel = etree.Element("ABSTRACTCHANNEL")
                    ElementChannel.set("name", "%s_%s"%(channel.label, channelIndex))
                    ElementChannel.set("k",    "%s"%(channel.cost))
                    ElementChannel.set("p",    "%s"%(channel.power))
                    ElementChannel.set("w",    "%s"%(channel.wireless))

                    ElementChannelNodes     = etree.Element("N")
                    ElementChannelDataFlows = etree.Element("F")

                    SetOfConnectingNodes = set()
                    for placedDataFlow in PlacedDataFlows:
                        SourceDeploymentNode = placedDataFlow.source.getDeployedIn()
                        TargetDeploymentNode = placedDataFlow.target.getDeployedIn()

                        SetOfConnectingNodes.add("%s_%s_%s"%(SourceDeploymentNode[0], SourceDeploymentNode[1], SourceDeploymentNode[2]))
                        SetOfConnectingNodes.add("%s_%s_%s"%(TargetDeploymentNode[0], TargetDeploymentNode[1], TargetDeploymentNode[2]))

                        ElementChannelDataflow = etree.Element("DATAFLOW")
                        ElementChannelDataflow.set("name", "%s"%(placedDataFlow))
                        ElementChannelDataFlows.append(ElementChannelDataflow)

                    for connectedNode in SetOfConnectingNodes:
                        ElementChannelSourceNode = etree.Element("NODE")
                        ElementChannelSourceNode.set("name", "%s"%(connectedNode))
                        ElementChannelNodes.append(ElementChannelSourceNode)

                    ElementChannel.append(ElementChannelNodes)
                    ElementChannel.append(ElementChannelDataFlows)

                    ElementCapacity = etree.Element("CAPACITY")
                    ElementCapacity.set("delay",      "%s"%(channel.delay))
                    ElementCapacity.set("error_rate", "%s"%(channel.error))
                    ElementCapacity.set("throughput", "%s"%(channel.bandwidth))
                    ElementChannel.append(ElementCapacity)

                    ElementChannels.append(ElementChannel)

        for zone in self.ZoneList:
            ElementZone = etree.Element("ZONE")
            ElementZone.set("name", "%s"%(zone.label))
            ElementZone.set("xi",   "(%s,%s,%s)"%(zone.x, zone.y, zone.z))
            ElementZones.append(ElementZone)
            ElementZoneNodes = etree.Element("N")
            ElementZone.append(ElementZoneNodes)
            for node in self.NodeList:
                for nodeIndex in self.indexSetOfClonesOfNodesInArea[node, zone]:
                    PlacedTasks = []
                    for task in node.getAllowedTask():
                        if(task.zone == zone):
                            if self.SolW.get((task, node, nodeIndex), False):
                                PlacedTasks.append(task)
                    if(len(PlacedTasks) > 0):
                        ElementNode = etree.Element("NODE")
                        ElementNode.set("name", "%s_%s_%s"%(node.label, nodeIndex, zone.label))
                        ElementZoneNodes.append(ElementNode)

        for contiguity in self.ContiguityList:
            ElementContiguity = etree.Element("CONTIGUITY")
            ElementContiguity.set("name", "C_%s_%s_%s"%(contiguity[0], contiguity[1], contiguity[2]))
            ElementContiguities.append(ElementContiguity)

            ElementZoneOne = etree.Element("Z1")
            ElementZoneOne.set("name", "%s"%(contiguity[0]))
            ElementContiguity.append(ElementZoneOne)

            ElementZoneTwo = etree.Element("Z2")
            ElementZoneTwo.set("name", "%s"%(contiguity[1]))
            ElementContiguity.append(ElementZoneTwo)

            ElementResistance = etree.Element("R")
            ElementResistance.set("added_delay",           "0")
            ElementResistance.set("added_error_rate",      "0")
            ElementResistance.set("power_red_factor",      "0")
            ElementResistance.set("throughput_red_factor", "0")
            #ElementResistance.set("added_delay", "%s"%(self.ContiguityList.get(contiguity).conductance))
            #ElementResistance.set("added_error_rate", "%s"%(self.ContiguityList.get(contiguity).conductance))
            #ElementResistance.set("power_red_factor", "%s"%(self.ContiguityList.get(contiguity).conductance))
            #ElementResistance.set("throughput_red_factor", "%s"%(self.ContiguityList.get(contiguity).conductance))
            ElementContiguity.append(ElementResistance)

        printedTree = minidom.parseString(etree.tostring(ElementRoot, encoding='unicode'))
        xmlFile = open('./TestCase.xml', 'w+')
        xmlFile.write(printedTree.toprettyxml(indent='    '))

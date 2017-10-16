from lxml import etree
from lxml.builder import ElementMaker
from xml.dom import minidom

class TechLibPrinter:
    def __init__(self,
                 NodeList,
                 ChannelList):
        self.NodeList = NodeList
        self.ChannelList = ChannelList
        print("# TechLibPrinter instantiated...")

    def printTechLib(self):
        print("###############################################################################")
        xmlTechlib  = etree.Element("TECHLIB")
        xmlNodes    = etree.Element("NODES")
        xmlChannels = etree.Element("ABSTRACTCHANNELS")

        xmlTechlib.append(xmlNodes)
        xmlTechlib.append(xmlChannels)

        for node in self.NodeList:
            xmlNode = etree.Element("NODE")
            xmlNode.set("k",    "%s"%(node.cost))
            xmlNode.set("m",    "%s"%(node.mobile))
            xmlNode.set("name", "%s"%(node.label))
            xmlNode.set("p",    "%s"%(node.power))

            xmlNodeCapCpu = etree.Element("CAPACITY")
            xmlNodeCapCpu.set("gamma", "0")
            xmlNodeCapCpu.set("name",  "cpu")
            xmlNodeCapCpu.set("value", "%s"%(node.size))
            xmlNode.append(xmlNodeCapCpu)

            xmlNodeCapMem = etree.Element("CAPACITY")
            xmlNodeCapMem.set("gamma", "0")
            xmlNodeCapMem.set("name",  "memory")
            xmlNodeCapMem.set("value", "%s"%(node.size))
            xmlNode.append(xmlNodeCapMem)
            xmlNodes.append(xmlNode)

        for channel in self.ChannelList:
            xmlChannel = etree.Element("ABSTRACTCHANNEL")
            xmlChannel.set("k",    "%s"%(channel.cost))
            xmlChannel.set("name", "%s"%(channel.label))
            xmlChannel.set("w",    "%s"%(channel.wireless))
            xmlChannel.set("p",    "%s"%(channel.power))

            xmlChannelCap = etree.Element("CAPACITY")
            xmlChannelCap.set("delay",      "%s"%(channel.delay))
            xmlChannelCap.set("error_rate", "%s"%(channel.error))
            xmlChannelCap.set("throughput", "%s"%(channel.bandwidth))
            xmlChannel.append(xmlChannelCap)
            xmlChannels.append(xmlChannel)

        printedTree = minidom.parseString(etree.tostring(xmlTechlib, encoding='unicode'))
        xmlFile = open('./TestCase.techlib.xml', 'w+')
        xmlFile.write(printedTree.toprettyxml(indent='    '))

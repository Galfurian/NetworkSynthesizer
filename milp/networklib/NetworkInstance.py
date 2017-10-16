from Node import Node
from Channel import Channel
from Zone import Zone
from Contiguity import Contiguity
from Task import Task
from DataFlow import DataFlow


class NetworkInstance:
    def __init__(self):
        self.channels = []
        self.nodes = []
        self.zones = []
        self.contiguities = {}
        self.tasks = []
        self.data_flows = []

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
        self.data_flows.append(data_flow)

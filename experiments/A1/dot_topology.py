import json
import os
import random

import networkx as nx
from SimPlacement.helpers.topology_generator import TopologyGeneratorHelper
from SimPlacement.setup import Setup
from SimPlacement.topology import Topology


zones = TopologyGeneratorHelper.load_yml_file("./files/40_1_topo.yml")

text = ""
relation = []
for zone in zones['zones']:
    z = zones['zones'][zone]

    if 'parent_zone' in z:
        relation.append("{} -> {}".format(z['parent_zone'], zone))

print("digraph D {{ {} }}".format("\n ".join(relation)))


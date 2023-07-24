import random

import networkx as nx
from beautifultable import BeautifulTable
from SimPlacement.helper import Helper

from SPEED.entities.zone import Zone


class SimulationHelper(Helper):

    @staticmethod
    def print_environment_topology(environment):
        """
        Print the zones, zone parent, domains and nodes of the environment.

        :param environment: The environment simulation.
        :return:
        """

        table = BeautifulTable()

        for zone_name, zone in environment['zones'].items():

            aux_nodes = []
            if zone.zone_type == Zone.TYPE_COMPUTE:
                nodes = environment['domains'][zone.domain_name].nodes.values()
                for node in nodes:
                    aux_nodes.append(node.name)

            aux_children = []
            if zone.zone_type == Zone.TYPE_AGGREGATION:
                aux_children = zone.child_zone_names

            table.rows.append([
                zone.name,
                zone.zone_type[0:5],
                zone.parent_zone_name,
                ", ".join(aux_children),
                zone.domain_name,
                ", ".join(aux_nodes)
            ])

        table.columns.header = [
            "Zone",
            "Type",
            "Parent",
            "Child's",
            "Domain",
            "Nodes"
        ]

        print("\n")
        print(table)

    @staticmethod
    def zone_topology_generation(size: int, seed: int = random.randint(0, 100)):
        """
        Generate a random tree that will express the zone topology
        used in the simulation.

        :param size: the size of the zone topology
        :param seed: the seed used to generate the topology
        :return: YAML with the topology

            zones:
              A_4:
                zone_type: "aggregation"
                parent_zone: "A_6"
              C_10:
                zone_type: "compute"
                parent_zone: "A_4"
                domain: "dom_9"
        """

        G: nx.DiGraph = nx.random_tree(n=size, seed=seed, create_using=nx.DiGraph)

        leafs = [x for x in G.nodes if G.in_degree(x) == 1 and G.out_degree(x) == 0]

        topo = {
            "zones": {}
        }

        for node in G.nodes:
            zone_name = ""
            if node not in leafs:
                zone_type="aggregation"
                zone_name = "A_{}".format(node)

            else:
                zone_type = "compute"
                zone_name = "C_{}".format(node)

            predecessors = [pred for pred in G.predecessors(node)]

            if predecessors:
                parent_zone = "A_{}".format(predecessors[0])
            else:
                parent_zone = ""

            topo['zones'][zone_name] = {
                "zone_type": zone_type,
                "parent_zone": parent_zone
            }

            # Remove the parent zone for the root
            if not parent_zone:
                del(topo['zones'][zone_name]['parent_zone'])

        return topo, G

import random

import networkx as nx
from beautifultable import BeautifulTable
from SimPlacement.helper import Helper

from SPEED.entities.zone import Zone
from SPEED.helpers.zone import ZoneHelper


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

    # @staticmethod
    # def zone_topology_generation(size: int):
    #     """
    #     Generate a random tree that will express the aggregation zone
    #     topology used in the simulation.
    #
    #     The compute zones will be defined inside the domain gene
    #
    #     :param size: Size of the zone topology
    #     :return: YAML Topology, DiGraph, List of leafs
    #
    #         zones:
    #           A_4:
    #             zone_type: "aggregation"
    #             parent_zone: "A_6"
    #           C_10:
    #             zone_type: "compute"
    #             parent_zone: "A_4"
    #             domain: "dom_9"
    #     """
    #
    #     # G: nx.DiGraph = nx.random_tree(n=size, seed=seed, create_using=nx.DiGraph)
    #     # G = nx.erdos_renyi_graph(size, 0.1)
    #     # # G = nx.complete_graph(size, create_using=nx.DiGraph)
    #     # G = nx.minimum_spanning_tree(G)
    #
    #     G = ZoneHelper.generate_random_tree_with_max_height(size)
    #
    #     # leafs = [x for x in G.nodes if G.in_degree(x) == 1 and G.out_degree(x) == 0]
    #     leafs = [node for node, degree in G.degree() if degree == 1]
    #
    #     topo = {
    #         "zones": {}
    #     }
    #
    #     for node in G.nodes:
    #         zone_name = ""
    #         if node not in leafs:
    #             zone_type="aggregation"
    #             zone_name = "A_{}".format(node)
    #
    #         else:
    #             zone_type = "compute"
    #             zone_name = "C_{}".format(node)
    #
    #         predecessors = [pred for pred in G.predecessors(node)]
    #
    #         if predecessors:
    #             parent_zone = "A_{}".format(predecessors[0])
    #         else:
    #             parent_zone = ""
    #
    #         topo['zones'][zone_name] = {
    #             "zone_type": "{}".format(zone_type),
    #             "parent_zone": "{}".format(parent_zone)
    #         }
    #
    #         # Remove the parent zone for the root
    #         if not parent_zone:
    #             del(topo['zones'][zone_name]['parent_zone'])
    #
    #     return topo, G, leafs
    #
    # @staticmethod
    # def generate_topology_with_x_leafs(num_leafs: int, size: int = 0):
    #     """
    #     Create a topology with the specific leafs number.
    #
    #     :param size: The zones total.
    #     :param num_leafs: Leaf numbers required.
    #
    #     :return:
    #     """
    #     leafs = []
    #     zone_topology = ""
    #     while len(leafs) != num_leafs:
    #         zone_topology, G, leafs = SimulationHelper.zone_topology_generation(
    #             size=size
    #         )
    #
    #     return zone_topology, G, leafs

    @staticmethod
    def generate_zone_topology(max_height: int, num_aggregation_zones: int, domains: dict):
        """
        Generate a tree with a max_height

        Used to build the aggregation zone topology.

        :param max_height: Tree max height.
        :param num_aggregation_zones: Amount of aggregation zones.
        :param domains: Dict with the domains generated
        :return:
        """
        # generate the aggregation zones
        aggregation_zones = ZoneHelper.generate_random_tree_with_max_height(
            max_height=max_height,
            num_aggregation_zones=num_aggregation_zones
        )

        # find the aggregation zones that are leafs in the topology
        # the leafs must have at least one compute zone (domain) as chield
        leafs = [node for node, degree in aggregation_zones.degree() if degree == 1]

        # the number of leafs must be greater than the number of domains
        if len(domains) < len(leafs):
            raise TypeError("The number of domains {} is lower than the number of leafs {} zoned in the topology. Increase the number of generated domains in the simulation.".format(len(domains), len(leafs)))

        topo = {
            "zones": {}
        }

        # Add the aggregation zones in the zone topology
        list_aggregation_zones = list(aggregation_zones.nodes)
        for node in list_aggregation_zones:
            zone_name = "A_{}".format(node)

            predecessors = [pred for pred in aggregation_zones.predecessors(node)]

            if predecessors:
                parent_zone = "A_{}".format(predecessors[0])
            else:
                parent_zone = ""

            topo['zones'][zone_name] = {
                "zone_type": "aggregation",
                "parent_zone": "{}".format(parent_zone)
            }

            if topo['zones'][zone_name]["parent_zone"] == "":
                del(topo['zones'][zone_name]["parent_zone"])

        # bind the domain in the leaf aggregation zones
        domains_name = list(domains.keys())
        for leaf in leafs:
            domain_name:str = domains_name.pop()
            name = domain_name.split("_")
            zone_name = "C_{}".format(name[1])

            topo['zones'][zone_name] = {
                "zone_type": "compute",
                "parent_zone": "A_{}".format(leaf),
                "domain": domain_name
            }

        # The intermediate aggregation zones
        internal_zones = [x for x in list(aggregation_zones.nodes) if x not in leafs]

        for leaf in internal_zones:
            # all the domains were binded to an aggregation zone
            if not domains_name:
                continue

            domain_name:str = domains_name.pop()
            name = domain_name.split("_")
            zone_name = "C_{}".format(name[1])

            topo['zones'][zone_name] = {
                "zone_type": "compute",
                "parent_zone": "A_{}".format(leaf),
                "domain": domain_name
            }

        # The remainder domains will be random distributed
        for domain_name in domains_name:

            name = domain_name.split("_")
            zone_name = "C_{}".format(name[1])

            random_aggregation_zone_name = "A_{}".format(random.choice(list_aggregation_zones))

            topo['zones'][zone_name] = {
                "zone_type": "compute",
                "parent_zone": random_aggregation_zone_name,
                "domain": domain_name
            }

        return topo
import random

from SimPlacement.entities.node import Node
from networkx.drawing.nx_pydot import graphviz_layout
from typing import Dict, List
from beautifultable import BeautifulTable

from SimPlacement.helper import Helper
from SimPlacement.entities.domain import Domain
from SPED.entities.zone import Zone
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import networkx as nx


class ZoneHelper(Helper):

    ZONE_ACCESS_COLOR = "#D5E8D4"
    ZONE_COMPUTE_COLOR = "#FFF2CC"
    ZONE_AGGREGATION_COLOR = "#DAE8FC"

    @staticmethod
    def load(data_file: str, environment: dict) -> Dict[str, Zone]:
        """
        Load all the zones defined in the configuration file.

        :param data_file: path to the config file.
        :param environment: The environment.
        :return: Dict with all the Zones.
        """

        data = Helper.load_yml_file(data_file)
        domains: Dict[str, Domain] = environment['domains']

        try:
            zone_data = data["zones"]
        except KeyError:
            raise TypeError("Config file does not have the field zones.")

        zones: Dict[str, Zone] = dict()

        for zone_name, zone in zone_data.items():

            # Verify if the zone type is valid
            if zone['zone_type'] not in Zone.VALID_TYPES:
                raise TypeError("The zone_type {} does not exist.".format(zone['zone_type']))

            extra = None
            if "extra_parameters" in zone:
                extra = zone["extra_parameters"]

            aux_parent_zone_name = None
            if 'parent_zone' in zone.keys():
                aux_parent_zone_name = zone['parent_zone']

                if aux_parent_zone_name not in zones.keys():
                    raise TypeError("The parent zone {} does not exist.".format(aux_parent_zone_name))

            domain_name = ""
            if 'domain' in zone.keys():
                domain_name = zone['domain']

            aux = Zone(
                name=zone_name,
                zone_type=zone['zone_type'],
                child_zone_names=[],
                parent_zone_name=aux_parent_zone_name,
                domain_name=domain_name,
                extra_parameters=extra
            )

            # Add the domain to the domain list
            zones[zone_name] = aux

        # Add child zones
        for zone_name, zone in zones.items():
            if zone.parent_zone_name:
                zones[zone.parent_zone_name].add_child_zone_name(zone_name)

        return zones

    @staticmethod
    def show(zone: Zone):  # pragma: no cover
        """
        Print the Zone.

        :param zone: The Zone object.
        :return:
        """
        if not type(zone) == Zone:
            raise TypeError("The zone must be a Zone object.")

        table = BeautifulTable()

        table.rows.append([zone.name])
        table.rows.append([zone.zone_type])
        table.rows.append([zone.domain_name])
        table.rows.append([zone.parent_zone_name])
        table.rows.append([", ".join(zone.child_zone_names)])

        table.rows.header = [
            "Zone",
            "Type",
            "Domain",
            "Parent",
            "Child's",
        ]

        print("\n")
        print(table)

    @staticmethod
    def build_zone_tree(zones: Dict[str, Zone]):
        """
        Build the zone tree.

        :param zones: The zone topology.
        :return:
        """

        graph: nx.Graph = nx.DiGraph()
        for zone_name, zone in zones.items():

            node_color = ZoneHelper.ZONE_ACCESS_COLOR

            if zone.zone_type == Zone.TYPE_COMPUTE:
                node_color = ZoneHelper.ZONE_COMPUTE_COLOR

            if zone.zone_type == Zone.TYPE_AGGREGATION:
                node_color = ZoneHelper.ZONE_AGGREGATION_COLOR

            graph.add_node(
                zone_name,
                zone_name=zone_name,
                zone_type=zone.zone_type,
                node_color=node_color
            )

            for child_zone_name in zone.child_zone_names:
                graph.add_edge(zone_name, child_zone_name)

        return graph

    @staticmethod
    def save_image(zones: Dict[str, Zone], title: str, file_name: str, img_width: int = 20, img_height: int = 20):  # pragma: no cover
        """
        Save an image of the topology.

        :param zones: The zone topology.
        :param title: The title of the image.
        :param file_name: Filename
        :param img_width: The image width.
        :param img_height: The image height.
        :return:
        """

        graph = ZoneHelper.build_zone_tree(zones)

        node_color = []

        for node_name in graph.nodes:
            node = graph.nodes[node_name]
            node_color.append(node['node_color'])

        legend_elements = list()

        legend_elements.append(
            Line2D([], [],
                   marker='o',
                   color=ZoneHelper.ZONE_ACCESS_COLOR,
                   markeredgecolor=ZoneHelper.ZONE_ACCESS_COLOR,
                   label="Access Zone",
                   markeredgewidth=1,
                   markersize=10)
        )

        legend_elements.append(
            Line2D([], [],
                   marker='o',
                   color=ZoneHelper.ZONE_COMPUTE_COLOR,
                   markeredgecolor=ZoneHelper.ZONE_COMPUTE_COLOR,
                   label="Compute Zone",
                   markeredgewidth=1,
                   markersize=10)
        )

        legend_elements.append(
            Line2D([], [],
                   marker='o',
                   color=ZoneHelper.ZONE_AGGREGATION_COLOR,
                   markeredgecolor=ZoneHelper.ZONE_AGGREGATION_COLOR,
                   label="Aggregation Zone",
                   markeredgewidth=1,
                   markersize=10)
        )

        plt.figure(figsize=(img_width, img_height))
        ax = plt.subplot(111)

        ax.legend(
            handles=legend_elements,
            loc='upper left',
            fontsize=18
        )

        if title != "":
            ax.set_title(title, fontsize=24)

        # pos = nx.spring_layout(graph)
        pos = graphviz_layout(graph, prog="dot")
        nx.draw(
            graph,
            pos,
            connectionstyle='arc3, rad = 0.15',
            node_color=node_color,
            linewidths=2,
            node_size=2000,
            font_size=12,
            with_labels=True,
            font_weight='normal',
            arrowsize=20
        )

        plt.tight_layout()
        plt.savefig(file_name, format="PNG")
        plt.close()

    @staticmethod
    def get_zone_names(zones: Dict[str, Zone], zone_type: str = Zone.TYPE_COMPUTE) -> List[str]:
        """
        Return the name of all zones of a type.

        :param zones: All the zones
        :param zone_type: The requested type

        :return:
        """
        names: List[str] = []

        for zone_name, zone in zones.items():
            if zone.zone_type == zone_type:
                names.append(zone_name)

        return names

    @staticmethod
    def get_random_node_from_zone(zone: Zone, environment) -> Node:
        """
        Return one node from the zone.

        If the zone is a compute zone it is a direct action.

        If the zone was a aggregation zone it is a recursive process.

        :param zone: The mother zone
        :param environment: The environment

        :return:
        """

        if zone.zone_type == Zone.TYPE_COMPUTE:
            nodes = environment['domains'][zone.domain_name].nodes
            possible_nodes = list(nodes.keys())

            if not possible_nodes:
                raise TypeError("The zone {} does not have nodes.".format(zone.name))

            node_name = random.choice(possible_nodes)
            node = environment['nodes'][node_name]
            return node

        possible_zones = []
        for zone_name in zone.child_zone_names:
            if environment['zones'][zone_name].zone_type == Zone.TYPE_ACCESS:
                continue
            possible_zones.append(zone_name)

        if not possible_zones:
            raise TypeError("The zone {} does not child zones.".format(zone.name))

        selected_child_zone = random.choice(possible_zones)

        cz = environment['zones'][selected_child_zone]

        return ZoneHelper.get_random_node_from_zone(
            zone=cz,
            environment=environment
        )

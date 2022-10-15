import random
from typing import Dict

from beautifultable import BeautifulTable

from SimPlacement.helper import Helper
from SimPlacement.entities.domain import Domain

from SPED.entities.sped import SPED
from SPED.entities.zone import Zone

from distinctipy import distinctipy
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import networkx as nx

import pydot
from networkx.drawing.nx_pydot import graphviz_layout


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

            domain = None
            node = None
            # Verify if the domain exists
            if 'domain' in zone.keys():
                if zone['domain'] not in domains.keys():
                    raise TypeError("The domain {} does not exist.".format(zone['domain']))

                domain = domains[zone['domain']]
                node = random.choice(list(domain.nodes.values()))

            extra = None
            if "extra_parameters" in zone:
                extra = zone["extra_parameters"]

            aux_sped = SPED(
                name='s_{}'.format(zone_name),
                domain=domain,
                node=node,
                zone_name=zone_name,
                environment=environment
            )

            aux_parent_zone_name = None
            if 'parent_zone' in zone.keys():
                aux_parent_zone_name = zone['parent_zone']

            aux = Zone(
                name=zone_name,
                zone_type=zone['zone_type'],
                sped=aux_sped,
                child_zone_names=[],
                parent_zone_name=aux_parent_zone_name,
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

        domain_name = ""
        if zone.sped.domain:
            domain_name = zone.sped.domain.name

        table.rows.append([zone.name])
        table.rows.append([zone.zone_type])
        table.rows.append([domain_name])
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

            graph.add_node(zone_name)

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

        for zone_name, zone in zones.items():
            if zone.zone_type == Zone.TYPE_ACCESS:
                node_color.append(ZoneHelper.ZONE_ACCESS_COLOR)
            if zone.zone_type == Zone.TYPE_COMPUTE:
                node_color.append(ZoneHelper.ZONE_COMPUTE_COLOR)
            if zone.zone_type == Zone.TYPE_AGGREGATION:
                node_color.append(ZoneHelper.ZONE_AGGREGATION_COLOR)

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
            loc='lower left',
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

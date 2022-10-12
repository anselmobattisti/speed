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

    @staticmethod
    def load(data_file: str, domains: Dict[str, Domain]) -> Dict[str, Zone]:
        """
        Load all the zones defined in the configuration file.

        :param data_file: path to the config file.
        :param domains: The domains available in the system.
        :return: Dict with all the Zones.
        """

        data = Helper.load_yml_file(data_file)

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
                zone_name=zone_name
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
        # default sample colors
        # sample_colors = ["#FF8167", "#FFB667", "#5AB2D3", "#5ADE8B", "#d55ade", "#ca67ff"]
        zone_access_color = "#D5E8D4"
        zone_compute_color = "#FFF2CC"
        zone_aggregation_color = "#DAE8FC"

        node_color = []
        graph: nx.Graph = nx.Graph()
        for zone_name, zone in zones.items():

            if zone.zone_type == Zone.TYPE_ACCESS:
                node_color.append(zone_access_color)

            if zone.zone_type == Zone.TYPE_COMPUTE:
                node_color.append(zone_compute_color)

            if zone.zone_type == Zone.TYPE_AGGREGATION:
                node_color.append(zone_aggregation_color)

            graph.add_node(zone_name)

            for child_zone_name in zone.child_zone_names:
                graph.add_edge(zone_name, child_zone_name)

        legend_elements = list()

        legend_elements.append(
            Line2D([], [],
                   marker='o',
                   color=zone_access_color,
                   markeredgecolor=zone_access_color,
                   label="Access Zone",
                   markeredgewidth=1,
                   markersize=10)
        )

        legend_elements.append(
            Line2D([], [],
                   marker='o',
                   color=zone_compute_color,
                   markeredgecolor=zone_compute_color,
                   label="Compute Zone",
                   markeredgewidth=1,
                   markersize=10)
        )

        legend_elements.append(
            Line2D([], [],
                   marker='o',
                   color=zone_aggregation_color,
                   markeredgecolor=zone_aggregation_color,
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

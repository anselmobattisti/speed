from beautifultable import BeautifulTable
from SimPlacement.helper import Helper

from SPED.entities.zone import Zone


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
                zone.zone_type,
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


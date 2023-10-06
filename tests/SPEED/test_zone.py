import os
import os.path
import random

import unittest

from typing import Dict

import networkx as nx
import matplotlib.pyplot as plt
from SimPlacement.helpers.topology_generator import TopologyGeneratorHelper

from SimPlacement.setup import Setup
from SPEED.entities.zone import Zone
from SPEED.helpers.simulation import SimulationHelper
from SPEED.helpers.zone import ZoneHelper


class ZoneTest(unittest.TestCase):

    entities_file = "{}/config/entities.yml".format(os.path.dirname(os.path.abspath(__file__)))
    log_path = "{}/logs".format(os.path.dirname(os.path.abspath(__file__)))
    environment = None
    zone_1 = None

    @classmethod
    def setUpClass(cls):
        cls.environment = Setup.load_entities(cls.entities_file)

        cls.zone_1 = Zone(
            name="z_1",
            zone_type=Zone.TYPE_AGGREGATION,
            child_zone_names=["z_2", "z_3"],
        )

        cls.zone_2 = Zone(
            name="z_2",
            zone_type=Zone.TYPE_COMPUTE,
            child_zone_names=[],
            parent_zone_name="z_1"
        )

    def test_create_zone(self):
        self.assertEqual("z_1", self.zone_1.name)
        self.assertEqual("z_1", self.zone_2.parent_zone_name)

    def test_build_zones_from_file(self):
        """
        Build the zone topology from the data loaded from the config file.
        """
        entities_file = "{}/config/entities_topology_build.yml".format(os.path.dirname(os.path.abspath(__file__)))
        zone_file = "{}/config/zone_topology.yml".format(os.path.dirname(os.path.abspath(__file__)))

        environment = Setup.load_entities(entities_file)

        zones: Dict[str, Zone] = ZoneHelper.load(
            data_file=zone_file,
            environment=environment
        )

        self.assertEqual("aggregation", zones['z_1'].zone_type)
        self.assertEqual("z_1", zones['z_1'].name)
        self.assertEqual(2, len(zones['z_2'].child_zone_names))
        self.assertEqual("z_3", zones['z_8'].parent_zone_name)
        self.assertEqual("dom_5", zones['z_8'].domain_name)

    def test_build_zones_from_file_4_levels(self):
        """
        Build the zone topology with 4 levels
        """
        entities_file = "{}/config/entities_topology_build.yml".format(os.path.dirname(os.path.abspath(__file__)))
        zone_file = "{}/config/zone_topology_3.yml".format(os.path.dirname(os.path.abspath(__file__)))

        environment = Setup.load_entities(entities_file)

        zones: Dict[str, Zone] = ZoneHelper.load(
            data_file=zone_file,
            environment=environment
        )

        self.assertEqual("aggregation", zones['z_1'].zone_type)

    def test_build_save_image(self):
        """
        Build the zone topology from the data loaded from the config file.
        """
        entities_file = "{}/config/entities_topology_build.yml".format(os.path.dirname(os.path.abspath(__file__)))
        zone_file = "{}/config/zone_topology_2.yml".format(os.path.dirname(os.path.abspath(__file__)))

        environment = Setup.load_entities(entities_file)

        zones: Dict[str, Zone] = ZoneHelper.load(
            data_file=zone_file,
            environment=environment
        )

        img_file = "{}/img/zone_topology_2.png".format(os.path.dirname(os.path.abspath(__file__)))
        ZoneHelper.save_image(
            zones=zones,
            title="Zones Topology 2",
            file_name=img_file,
            img_width=15,
            img_height=15
        )

        self.assertTrue(os.path.isfile(img_file))

        # remove the created file.
        os.remove(img_file)

    def test_zone_names(self):
        """
        Get all the name based on a type
        """
        entities_file = "{}/config/entities_topology_build.yml".format(os.path.dirname(os.path.abspath(__file__)))
        zone_file = "{}/config/zone_topology.yml".format(os.path.dirname(os.path.abspath(__file__)))

        environment = Setup.load_entities(entities_file)

        zones: Dict[str, Zone] = ZoneHelper.load(
            data_file=zone_file,
            environment=environment
        )

        compute_zone_names = ZoneHelper.get_zone_names(
            zones=zones
        )

        aggregation_zone_names = ZoneHelper.get_zone_names(
            zones=zones,
            zone_type=Zone.TYPE_AGGREGATION
        )

        self.assertEqual(['z_4', 'z_5', 'z_6', 'z_7', 'z_8'], compute_zone_names)
        self.assertEqual(['z_1', 'z_2', 'z_3'], aggregation_zone_names)

    def test_build_dot_from_zone_file(self):
        """
        Test the function that create a string used to plot the zone topology
        using dot.
        :return:
        """
        zone_file = "{}/config/zone_topology.yml".format(os.path.dirname(os.path.abspath(__file__)))

        dot_str = ZoneHelper.build_dot_from_zone_file(zone_file)

        self.assertEqual(207, len(dot_str))

    def test_get_random_compute_zone(self):
        """
        Test the process of getting a random compute zone bellow a certain zone.
        :return:
        """
        random.seed(1)

        entities_file = "{}/config/entities_topology_build.yml".format(os.path.dirname(os.path.abspath(__file__)))
        zone_file = "{}/config/zone_topology.yml".format(os.path.dirname(os.path.abspath(__file__)))

        environment = Setup.load_entities(entities_file)

        zones = ZoneHelper.load(
            data_file=zone_file,
            environment=environment
        )

        zt = ZoneHelper.build_zone_tree(zones)

        cz = ZoneHelper.get_random_compute_zone(
            mother_zone=zones['z_3'],
            zone_tree=zt
        )

        self.assertEqual(cz, 'z_7')

    def test_generate_zone_topology_zoo(self):
        """
        Test the creation of the topology hierarchy based on the zoo topology file.
        """
        path = os.path.dirname(os.path.abspath(__file__))

        num_domain = 1

        i = 1

        # fe  = "{}/config/zoo_topology/config_entities.yml".format(path)
        # oft = "{}/files/{}_{}_topo.yml".format(path, num_domain, i)
        #
        # config_topology = dict()
        # config_topology['num_vnfs'] = 10
        # config_topology['num_sfcs'] = 10
        # config_topology['num_nodes'] = 1000
        # config_topology['num_ues'] = 10
        # config_topology['num_sfc_requests'] = 10
        # config_topology['num_domains'] = 63
        #
        # aux = dict()
        # aux['inter_domain'] = 0.02
        # aux['intra_domain'] = 0.30
        # config_topology['link_probability'] = aux
        #
        # TopologyGeneratorHelper.generate(
        #     config_file=fe,
        #     output_file=ofe,
        #     config_topology=config_topology
        # )
        #
        # generated_environment =  TopologyGeneratorHelper.load_yml_file(
        #     data_file=ofe
        # )

        zoo_topology_file = "{}/config/zoo_topology/topology-zoo.org_files_Internode.gml".format(path)
        ofe = "{}/config/zoo_topology/files/environment.yml".format(path)
        topo_file = "{}/config/zoo_topology/files/topo.yml".format(path)

        SimulationHelper.convert_environment_using_topology_zoo(
            zoo_topology=zoo_topology_file,
            zone_root=10,
            environment_file=ofe,
            topo_file = topo_file
        )

        self.assertEqual(True, False)

    def test_import_zoo_topology(self):
        """
        Import the zoo topology to be executed in the simulation.
        :return:
        """
        # Load the GML file
        G = nx.read_gml("config/zoo_topology/topology-zoo.org_files_Internode.gml")

        # Compute the centrality of all the nodes in the topology
        centrality = nx.degree_centrality(G)

        # Sort the nodes by the centrality, the first nodes has higher centrality
        s = sorted(centrality.items(), key=lambda x: x[1], reverse=True)

        # How many topologies to create?
        zone_limit = 10

        num_sfc_requests = [5, 10]

        path = os.path.dirname(os.path.abspath(__file__))

        fe  = "{}/config/zoo_topology/config_entities.yml".format(path)
        # ofe = "{}/config/zoo_topology/files/{}_{}.yml".format(path, num_domain, i)
        # oft = "{}/files/{}_{}_topo.yml".format(path, num_domain, i)

        # For each topology do the task
        for k, v in s[:zone_limit]:
            # Construct the tree (topology hierarchic) using the breadth-first-search
            tree = nx.bfs_tree(G, k)

            # Save the tree image in the img folder
            p = nx.drawing.nx_pydot.to_pydot(tree)
            p.write_png('./config/zoo_topology/img/{}.png'.format(k))

            # # All the nodes in the tree graph are Aggregation zones
            #
            # # For each Aggregation zone, one compute zone will be attached
            #
            # for num_sfc_request in num_sfc_requests:
            #
            #     config_topology = dict()
            #     config_topology['num_vnfs'] = 10
            #     config_topology['num_sfcs'] = 10
            #     config_topology['num_nodes'] = 1000
            #     config_topology['num_ues'] = 10
            #     config_topology['num_sfc_requests'] = num_sfc_request
            #     config_topology['num_domains'] = len(G.nodes)
            #
            #     aux = dict()
            #     aux['inter_domain'] = 0.02
            #     aux['intra_domain'] = 0.30
            #     config_topology['link_probability'] = aux
            #
            #     TopologyGeneratorHelper.generate(
            #         config_file=fe,
            #         output_file=ofe,
            #         config_topology=config_topology
            #     )
            #
            #     # load the generated environment
            #     topology = TopologyGeneratorHelper.load_yml_file(
            #         data_file=ofe
            #     )
            #
            #     zone_topology = SimulationHelper.generate_zone_topology_zoo(
            #         num_aggregation_zones=num_aggregation_zones[j],
            #         max_height=max_height[j],
            #         domains=topology['domains']
            #     )

                # zone_topology = SimulationHelper.generate_zone_topology(
                #     num_aggregation_zones=num_aggregation_zones[j],
                #     max_height=max_height[j],
                #     domains=topology['domains']
                # )
                #
                # TopologyGeneratorHelper.save_file(
                #     output_file=oft,
                #     data=zone_topology
                # )

        self.assertEqual(True, True)

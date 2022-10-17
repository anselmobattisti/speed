import os
import unittest
from typing import Dict
import simpy
import networkx as nx

from SimPlacement.entities.domain import Domain
from SimPlacement.entities.node import Node
from SimPlacement.entities.vnf_instance import VNFInstance
from SimPlacement.setup import Setup
from SPED.entities.zone import Zone
from SPED.helpers.zone import ZoneHelper
from SPED.types import InfrastructureData
from SPED.helpers.sped import SPEDHelper
from SPED.simulation import SPEDSimulation
from SimPlacement.helper import Helper


class SPEDTest(unittest.TestCase):

    def test_select_zone_manager(self):
        """
        Verify if the zone manager zone selection is working
        :return:
        """
        env = simpy.Environment()
        entities_file = "{}/config/entities_topology_build.yml".format(os.path.dirname(os.path.abspath(__file__)))
        zone_file = "{}/config/zone_topology.yml".format(os.path.dirname(os.path.abspath(__file__)))
        simulation_file = "{}/config/simulation_config.yml".format(os.path.dirname(os.path.abspath(__file__)))

        environment = Setup.load_entities(
            entities_file=entities_file
        )

        environment['zones'] = ZoneHelper.load(
            data_file=zone_file,
            environment=environment
        )

        config = Helper.load_yml_file(
            data_file=simulation_file
        )

        simulation = SPEDSimulation(
            env=env,
            config=config["simulation"],
            environment=environment
        )

        simulation.setup()

        simulation.update_aggregated_data()

        sr_1 = environment['sfc_requests']['sr_1']
        sr_2 = environment['sfc_requests']['sr_2']
        sr_3 = environment['sfc_requests']['sr_3']

        z_sr1 = simulation.select_zone_manager(sr_1)
        z_sr2 = simulation.select_zone_manager(sr_2)
        z_sr3 = simulation.select_zone_manager(sr_3)

        simulation.update_aggregated_data()

        self.assertEqual("z_2", z_sr1)
        self.assertEqual("z_1", z_sr2)
        self.assertEqual("z_2", z_sr3)

    def test_select_zone_manager_4_level(self):
        """
        Verify if the zone manager zone selection is working
        :return:
        """
        env = simpy.Environment()
        entities_file = "{}/config/entities_topology_build.yml".format(os.path.dirname(os.path.abspath(__file__)))
        zone_file = "{}/config/zone_topology_3.yml".format(os.path.dirname(os.path.abspath(__file__)))
        simulation_file = "{}/config/simulation_config.yml".format(os.path.dirname(os.path.abspath(__file__)))

        environment = Setup.load_entities(
            entities_file=entities_file
        )

        environment['zones'] = ZoneHelper.load(
            data_file=zone_file,
            environment=environment
        )

        config = Helper.load_yml_file(
            data_file=simulation_file
        )

        simulation = SPEDSimulation(
            env=env,
            config=config["simulation"],
            environment=environment
        )

        simulation.setup()

        simulation.update_aggregated_data()

        sr_6 = environment['sfc_requests']['sr_6']
        z_sr6 = simulation.select_zone_manager(sr_6)
        self.assertEqual("z_0", z_sr6)

    def test_update_aggregated_data(self):
        """
        Update all the aggregated data from all the zones
        :return:
        """
        env = simpy.Environment()
        entities_file = "{}/config/entities_topology_build.yml".format(os.path.dirname(os.path.abspath(__file__)))
        zone_file = "{}/config/zone_topology_3.yml".format(os.path.dirname(os.path.abspath(__file__)))
        simulation_file = "{}/config/simulation_config.yml".format(os.path.dirname(os.path.abspath(__file__)))

        environment = Setup.load_entities(
            entities_file=entities_file
        )

        environment['zones'] = ZoneHelper.load(
            data_file=zone_file,
            environment=environment
        )

        config = Helper.load_yml_file(
            data_file=simulation_file
        )

        simulation = SPEDSimulation(
            env=env,
            config=config["simulation"],
            environment=environment
        )

        simulation.setup()

        simulation.update_aggregated_data()

        z_0: Zone = environment['zones']['z_0']
        data = z_0.sped.aggregate_date()
        self.assertEqual(375.0, data['n_3_vnf_1']['cost'])

    def test_setup(self):
        """
        Test the setup simulation
        """
        env = simpy.Environment()
        entities_file = "{}/config/entities_topology_build.yml".format(os.path.dirname(os.path.abspath(__file__)))
        zone_file = "{}/config/zone_topology.yml".format(os.path.dirname(os.path.abspath(__file__)))
        simulation_file = "{}/config/simulation_config.yml".format(os.path.dirname(os.path.abspath(__file__)))

        environment = Setup.load_entities(
            entities_file=entities_file
        )

        environment['zones'] = ZoneHelper.load(
            data_file=zone_file,
            environment=environment
        )

        config = Helper.load_yml_file(
            data_file=simulation_file
        )

        simulation = SPEDSimulation(
            env=env,
            config=config["simulation"],
            environment=environment
        )

        simulation.setup()

        simulation.update_aggregated_data()

        sr_1 = environment['sfc_requests']['sr_1']

        simulation.distributed_placement_process(
            sfc_request=sr_1
        )

        self.assertEqual(5, len(simulation.domain_zone))

    def test_select_zone_manager_parent(self):
        """
        Select the zone manager until the parent zone
        :return:
        """
        env = simpy.Environment()
        entities_file = "{}/config/entities_topology_build.yml".format(os.path.dirname(os.path.abspath(__file__)))
        zone_file = "{}/config/zone_topology_3.yml".format(os.path.dirname(os.path.abspath(__file__)))
        simulation_file = "{}/config/simulation_config.yml".format(os.path.dirname(os.path.abspath(__file__)))

        environment = Setup.load_entities(
            entities_file=entities_file
        )

        environment['zones'] = ZoneHelper.load(
            data_file=zone_file,
            environment=environment
        )

        config = Helper.load_yml_file(
            data_file=simulation_file
        )

        simulation = SPEDSimulation(
            env=env,
            config=config["simulation"],
            environment=environment
        )

        simulation.setup()

        simulation.update_aggregated_data()

        # sr_6 = environment['sfc_requests']['sr_6']
        # z_sr6 = simulation.select_zone_manager(sr_6)

        sr_7 = environment['sfc_requests']['sr_7']
        z_sr7 = simulation.select_zone_manager(sr_7)
        #
        # img_file = "{}/img/zone_topology.png".format(os.path.dirname(os.path.abspath(__file__)))
        # ZoneHelper.save_image(
        #     zones=environment['zones'],
        #     title="Zones Topology 4",
        #     file_name=img_file,
        #     img_width=15,
        #     img_height=15
        # )

        self.assertEqual("z_0", z_sr7)

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

        sr_1 = environment['sfc_requests']['sr_1']
        sr_2 = environment['sfc_requests']['sr_2']
        sr_3 = environment['sfc_requests']['sr_3']

        z_sr1 = simulation.select_zone_manager(sr_1)
        z_sr2 = simulation.select_zone_manager(sr_2)
        z_sr3 = simulation.select_zone_manager(sr_3)

        self.assertEqual("z_4", z_sr1)
        self.assertEqual("z_1", z_sr2)
        self.assertEqual("z_2", z_sr3)

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

        sr_1 = environment['sfc_requests']['sr_1']

        simulation.distributed_placement_process(
            sfc_request=sr_1
        )

        self.assertTrue(True)
        # z_2 = zones['z_2']
        #
        # z_4 = zones['z_4']
        # aggregate_date_z4 = z_4.sped.aggregate_date()
        # z_2.sped.update_child_zone_aggregated_data("z_4", aggregate_date_z4)
        #
        # z_5 = zones['z_5']
        # aggregate_date_z5 = z_5.sped.aggregate_date()
        # z_2.sped.update_child_zone_aggregated_data("z_5", aggregate_date_z5)
        #
        # aggregate_date_z2 = z_2.sped.aggregate_date()
        # z_1 = zones['z_1']
        # for zone_name in ['z_2', 'z_3']:
        #     z: Zone = zones[zone_name]
        #
        #     for child_zone_name in z.child_zone_names:
        #         c_z: Zone = zones[child_zone_name]
        #
        #         z.sped.update_child_zone_aggregated_data(
        #             zone_name=child_zone_name,
        #             child_zone_aggregated_data=c_z.sped.aggregate_date()
        #         )
        #     z_1.sped.update_child_zone_aggregated_data(
        #         zone_name=zone_name,
        #         child_zone_aggregated_data=z.sped.aggregate_date()
        #     )
        #
        # aggregate_date = z_1.sped.aggregate_date()
        # print(" a ")
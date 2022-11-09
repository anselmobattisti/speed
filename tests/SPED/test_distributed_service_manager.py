import os
import unittest
import simpy

from typing import Dict
import networkx as nx

from SimPlacement.entities.domain import Domain
from SimPlacement.entities.node import Node
from SimPlacement.entities.vnf_instance import VNFInstance
from SPED.entities.zone import Zone
from SPED.helpers.simulation import SimulationHelper
from SPED.types import InfrastructureData
from SPED.helpers.sped import SPEDHelper

from SimPlacement.setup import Setup
from SPED.helpers.zone import ZoneHelper
from SPED.simulation import SPEDSimulation
from SimPlacement.helper import Helper


class DistributedServiceManagerTest(unittest.TestCase):

    def test_setup_distributed_service_manager(self):
        """
        Test if the setup creates for each zone a distributed service manager component.
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

        dsm = simulation.zdsm

        self.assertEqual(8, len(dsm))

    def test_get_random_node_from_zone(self):
        """
        Selects a random node to execute the distributed service manager component.
        """
        env = simpy.Environment()

        entities_file = "{}/config/entities_2_sfc_request.yml".format(os.path.dirname(os.path.abspath(__file__)))
        zone_file = "{}/config/zone_topology_4.yml".format(os.path.dirname(os.path.abspath(__file__)))
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

        dsm = simulation.zdsm

        self.assertEqual("n_2", dsm['z_0'].node.name)

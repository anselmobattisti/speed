import os
import unittest
from typing import Dict, List

import simpy
from SimPlacement.entities.node import Node
from SimPlacement.entities.vnf_instance import VNFInstance
from SimPlacement.entities.sfc_request import SFCRequest
from SimPlacement.helper import Helper
from SimPlacement.setup import Setup
from SPEED.entities.zone import Zone
from SPEED.helpers.zone import ZoneHelper
from SPEED.simulation import SPEEDSimulation
from SPEED.speed import SPEED
from SPEED.types import InfrastructureData
from SPEED.helpers.speed import SPEEDHelper
from SPEED.distributed_service_manager import DistributedServiceManager


class SPEEDTest(unittest.TestCase):

    entities_file = "{}/config/entities_topology_build.yml".format(os.path.dirname(os.path.abspath(__file__)))
    log_path = "{}/logs".format(os.path.dirname(os.path.abspath(__file__)))
    environment = None

    def test_compute_zone_data_collect(self):
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

        dsm = DistributedServiceManager(
            zone=zones['z_5'],
            environment=environment
        )

        speed = dsm.speed

        speed.aggregate_date()

        data_collected = speed.infrastructure_data

        dc_0: InfrastructureData = data_collected[0]

        self.assertEqual('z_5', dc_0['zone'])
        self.assertEqual('z_5', dc_0['zone'])

    def test_compute_zone_data_collect_creating_vnf_instance(self):
        """
        After build the topology create a new VNF Instance and verify if the cpu available changes.
        """
        entities_file = "{}/config/entities_topology_build.yml".format(os.path.dirname(os.path.abspath(__file__)))
        zone_file = "{}/config/zone_topology.yml".format(os.path.dirname(os.path.abspath(__file__)))

        environment = Setup.load_entities(entities_file)

        zones: Dict[str, Zone] = ZoneHelper.load(
            data_file=zone_file,
            environment=environment
        )

        # Create a VNF Instance in the node n_4
        n_4: Node = environment['nodes']['n_4']
        vnf1_name_teste: VNFInstance = n_4.create_vnf_instance(
            name='vnf1_name_teste',
            vnf_name='vnf_2'
        )

        vnf1_name_teste.set_status(
            value="active",
            status_to_count_resource_usage=["active"]
        )

        dsm = DistributedServiceManager(
            zone=zones['z_5'],
            environment=environment
        )

        speed = dsm.speed

        data_collected = speed.compute_zone_data_collect()

        dc_0: InfrastructureData = data_collected[0]
        self.assertEqual('z_5', dc_0['zone'])
        self.assertEqual(375, dc_0['cost'])

    def test_aggregate_infrastructure_data(self):
        """
        Aggregate the data in the compute zone.
        """
        entities_file = "{}/config/entities_topology_build.yml".format(os.path.dirname(os.path.abspath(__file__)))
        zone_file = "{}/config/zone_topology.yml".format(os.path.dirname(os.path.abspath(__file__)))

        environment = Setup.load_entities(entities_file)

        zones: Dict[str, Zone] = ZoneHelper.load(
            data_file=zone_file,
            environment=environment
        )

        # Create a VNF Instance in the node n_4
        n_4: Node = environment['nodes']['n_4']
        vnf1_name_teste: VNFInstance = n_4.create_vnf_instance(
            name='vnf1_name_teste',
            vnf_name='vnf_2'
        )

        vnf1_name_teste.set_status(
            value="active",
            status_to_count_resource_usage=["active"]
        )

        dsm = DistributedServiceManager(
            zone=zones['z_5'],
            environment=environment
        )

        speed = dsm.speed

        data_aggregate = speed.aggregate_infrastructure_data()

        self.assertEqual(18, len(data_aggregate.keys()))

    def test_vnf_segmentation(self):
        """
        Create the valid VNF Segments
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

        simulation = SPEEDSimulation(
            env=env,
            config=config["simulation"],
            environment=environment
        )

        simulation.setup()

        simulation.update_aggregated_data()

        segmentation_plans = SPEEDHelper.vnf_segmentation(
            vnf_names=['vnf_1', 'vnf_2']
        )

        segmentation_plans_2 = SPEEDHelper.vnf_segmentation(
            vnf_names=['vnf_1', 'vnf_2', 'vnf_3']
        )

        self.assertEqual(['vnf_1', 'vnf_2'], segmentation_plans['plan_0']['segments']['seg_0']['vnfs'])
        self.assertEqual(4, len(segmentation_plans_2))

    def test_select_vnf_segmentation(self):
        """
        Select the Segmentation plan that will be used.
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

        simulation = SPEEDSimulation(
            env=env,
            config=config["simulation"],
            environment=environment
        )

        simulation.setup()

        simulation.update_aggregated_data()

        # SFC ['vnf_1', 'vnf_2', 'vnf_3']
        sr_1: SFCRequest = environment['sfc_requests']['sr_1']
        zone_selected = simulation.select_zone_manager(
            sfc_request=sr_1
        )

        vnf_names: List[str] = list()

        for vnf in sr_1.sfc.vnfs:
            vnf_names.append(vnf.name)

        zone_manager: Zone = zone_selected['zone_manager']

        segmentation_plans = SPEEDHelper.vnf_segmentation(
            vnf_names=vnf_names
        )

        valid_plans_2 = simulation.zdsm[zone_manager.name].speed.valid_segmentation_plans(segmentation_plans)

        self.assertEqual(['plan_0', 'plan_1'], list(valid_plans_2.keys()))

    def test_vnfs_available(self):
        """
        Test the vnfs_available function.
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

        simulation = SPEEDSimulation(
            env=env,
            config=config["simulation"],
            environment=environment
        )

        simulation.setup()

        simulation.update_aggregated_data()

        speed = simulation.zdsm['z_0'].speed
        vnfs = speed.vnfs_available()

        speed_5 = simulation.zdsm['z_5'].speed
        vnfs_5 = speed.vnfs_available()

        self.assertEqual(['vnf_1', 'vnf_3', 'vnf_2'], vnfs)
        self.assertEqual(['vnf_1', 'vnf_3', 'vnf_2'], vnfs_5)

    def test_compute_zone_data_collect_resource_restriction(self):
        """
        After build the topology create a new VNF Instance and verify if the cpu available changes.
        """
        entities_file = "{}/config/resource_restriction/env.yml".format(os.path.dirname(os.path.abspath(__file__)))
        zone_file = "{}/config/resource_restriction/topo.yml".format(os.path.dirname(os.path.abspath(__file__)))

        environment = Setup.load_entities(entities_file)

        zones: Dict[str, Zone] = ZoneHelper.load(
            data_file=zone_file,
            environment=environment
        )

        # Create a VNF Instance in the node n_4
        n_1: Node = environment['nodes']['n_1']
        vnf1_name_teste: VNFInstance = n_1.create_vnf_instance(
            name='vnf1_name_teste',
            vnf_name='v_3'
        )

        vnf1_name_teste.set_status(
            value="active",
            status_to_count_resource_usage=["active"]
        )

        dsm = DistributedServiceManager(
            zone=zones['C_0'],
            environment=environment
        )

        speed = dsm.speed

        data_collected = speed.compute_zone_data_collect()

        self.assertEqual(True, False)

        # dc_0: InfrastructureData = data_collected[0]
        # self.assertEqual('z_5', dc_0['zone'])
        # self.assertEqual(375, dc_0['cost'])
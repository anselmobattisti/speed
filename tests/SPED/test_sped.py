import os
import unittest
from typing import Dict

from SimPlacement.entities.domain import Domain
from SimPlacement.entities.node import Node
from SimPlacement.entities.vnf_instance import VNFInstance
from SimPlacement.setup import Setup
from SPED.entities.zone import Zone
from SPED.helpers.zone import ZoneHelper
from SPED.types import InfrastructureData
from SPED.helpers.sped import SPEDHelper


class SPEDTest(unittest.TestCase):

    entities_file = "{}/config/entities_topology_build.yml".format(os.path.dirname(os.path.abspath(__file__)))
    log_path = "{}/logs".format(os.path.dirname(os.path.abspath(__file__)))
    environment = None

    def test_compute_zone_data_collect(self):
        """
        Build the zone topology from the data loaded from the config file
        """
        entities_file = "{}/config/entities_topology_build.yml".format(os.path.dirname(os.path.abspath(__file__)))
        zone_file = "{}/config/zone_topology.yml".format(os.path.dirname(os.path.abspath(__file__)))

        environment = Setup.load_entities(entities_file)
        domains = environment['domains']

        zones: Dict[str, Zone] = ZoneHelper.load(
            data_file=zone_file,
            domains=domains
        )

        z = zones['z_5']

        data_collected = z.sped.infrastructure_data

        dc_0: InfrastructureData = data_collected[0]
        self.assertEqual('z_5', dc_0['zone'])
        self.assertEqual('z_5', dc_0['zone'])

    def test_compute_zone_data_collect_creating_vnf_instance(self):
        """
        After build the topology create a new VNF Instance and verify if the cpu available changes
        """
        entities_file = "{}/config/entities_topology_build.yml".format(os.path.dirname(os.path.abspath(__file__)))
        zone_file = "{}/config/zone_topology.yml".format(os.path.dirname(os.path.abspath(__file__)))

        environment = Setup.load_entities(entities_file)
        domains = environment['domains']

        zones: Dict[str, Zone] = ZoneHelper.load(
            data_file=zone_file,
            domains=domains
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

        z = zones['z_5']

        data_collected = z.sped.compute_zone_data_collect()

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
        domains = environment['domains']

        zones: Dict[str, Zone] = ZoneHelper.load(
            data_file=zone_file,
            domains=domains
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

        z = zones['z_5']

        data_aggregate = z.sped.aggregate_infrastructure_data()

        aggregate_date

        for data in data_aggregate.values():
            SPEDHelper.show_aggregated_data(data)

        # dc_0: Agg = data_collected[0]
        # self.assertEqual('z_5', dc_0['zone'])
        # self.assertEqual(375, dc_0['cost'])

    def test_zone_aggregate_date(self):
        """
        Test the zone aggregated data
        """
        entities_file = "{}/config/entities_topology_build.yml".format(os.path.dirname(os.path.abspath(__file__)))
        zone_file = "{}/config/zone_topology.yml".format(os.path.dirname(os.path.abspath(__file__)))

        environment = Setup.load_entities(entities_file)

        zones: Dict[str, Zone] = ZoneHelper.load(
            data_file=zone_file,
            environment=environment
        )

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
        z_1 = zones['z_1']
        for zone_name in ['z_2', 'z_3']:
            z: Zone = zones[zone_name]

            for child_zone_name in z.child_zone_names:
                c_z: Zone = zones[child_zone_name]

                z.sped.update_child_zone_aggregated_data(
                    zone_name=child_zone_name,
                    child_zone_aggregated_data=c_z.sped.aggregate_date()
                )
            z_1.sped.update_child_zone_aggregated_data(
                zone_name=zone_name,
                child_zone_aggregated_data=z.sped.aggregate_date()
            )

        aggregate_date = z_1.sped.aggregate_date()
        print(" a ")

        # for data in aggregate_date.values():
        #     SPEDHelper.show_aggregated_data(data)

        # dc_0: Agg = data_collected[0]
        # self.assertEqual('z_5', dc_0['zone'])
        # self.assertEqual(375, dc_0['cost'])

    # def test_show_infrastructure_data(self):
    #     entities_file = "{}/config/entities_topology_build.yml".format(os.path.dirname(os.path.abspath(__file__)))
    #     zone_file = "{}/config/zone_topology.yml".format(os.path.dirname(os.path.abspath(__file__)))
    #
    #     environment = Setup.load_entities(entities_file)
    #     domains = environment['domains']
    #
    #     zones: Dict[str, Zone] = ZoneHelper.load(
    #         data_file=zone_file,
    #         domains=domains
    #     )
    #
    #     z = zones['z_5']
    #     data_collected = z.sped.compute_zone_data_collect()
    #
    #     dc_0: InfrastructureData = data_collected[0]
    #     SPEDHelper.show_infrastructure_data(dc_0)

import os
import unittest
import simpy


from SimPlacement.setup import Setup
from SPED.helpers.distributed_service import DistributedServiceHelper


class DistributedServiceTest(unittest.TestCase):

    def test_get_vnf_names_from_sfc_request(self):
        """
        Get the names of the VNFs of a SFC Request
        """
        env = simpy.Environment()
        entities_file = "{}/config/entities_topology_build.yml".format(os.path.dirname(os.path.abspath(__file__)))
        zone_file = "{}/config/zone_topology.yml".format(os.path.dirname(os.path.abspath(__file__)))
        simulation_file = "{}/config/simulation_config.yml".format(os.path.dirname(os.path.abspath(__file__)))

        environment = Setup.load_entities(
            entities_file=entities_file
        )

        vnf_names = DistributedServiceHelper.get_vnf_names_from_sfc_request(environment['sfc_requests']['sr_1'])

        self.assertEqual(['vnf_1', 'vnf_2'], vnf_names)

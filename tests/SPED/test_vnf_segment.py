import os
import unittest

from SimPlacement.setup import Setup
from SPED.entities.vnf_segment import VNFSegment


class VNFSegmentTest(unittest.TestCase):

    entities_file = "{}/config/entities.yml".format(os.path.dirname(os.path.abspath(__file__)))
    log_path = "{}/logs".format(os.path.dirname(os.path.abspath(__file__)))
    seg_1 = None
    environment = None

    @classmethod
    def setUpClass(cls):
        cls.environment = Setup.load_entities(cls.entities_file)
        vnfs = cls.environment['vnfs']

        cls.seg_1 = VNFSegment(
            name="seg_1",
            vnfs=[vnfs['vnf_2'], vnfs['vnf_1']],
            max_delay=10,
        )

    def test_create_vnf_segment(self):
        vnfs = self.environment['vnfs']
        self.assertEqual("seg_1", self.seg_1.name)
        self.assertEqual(10, self.seg_1.max_delay)
        self.assertEqual([vnfs['vnf_2'], vnfs['vnf_1']], self.seg_1.vnfs)

    def test_max_delay_error_0(self):
        try:
            self.seg_1.max_delay = 0
        except TypeError:
            pass
        else:
            self.fail("The max_delay must be greater than 0, was not detected")

    def test_max_delay_error_minus_one(self):
        try:
            self.seg_1.max_delay = -1
        except TypeError:
            pass
        else:
            self.fail("The max_delay must be greater than 0, was not detected")

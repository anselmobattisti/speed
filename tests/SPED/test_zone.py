import os
import unittest

from SimPlacement.setup import Setup
from SPED.entities.zone import Zone
from SPED.helpers.zone import ZoneHelper

class ZoneTest(unittest.TestCase):

    entities_file = "{}/config/entities.yml".format(os.path.dirname(os.path.abspath(__file__)))
    log_path = "{}/logs".format(os.path.dirname(os.path.abspath(__file__)))
    environment = None
    zone_1 = None

    @classmethod
    def setUpClass(cls):
        cls.environment = Setup.load_entities(cls.entities_file)
        domains = cls.environment['domains']

        cls.zone_1 = Zone(
            name="z_1",
            zone_type=Zone.TYPE_AGGREGATION,
            domain=domains['dom_1'],
            child_zone_names=["z_2", "z_3"],
        )

        cls.zone_2 = Zone(
            name="z_2",
            zone_type=Zone.TYPE_COMPUTE,
            domain=domains['dom_2'],
            child_zone_names=[],
            parent_zone_name="z_1"
        )

        cls.zone_3 = Zone(
            name="z_3",
            zone_type=Zone.TYPE_COMPUTE,
            domain=domains['dom_3'],
            child_zone_names=[],
            parent_zone_name="z_1"
        )

    def test_create_zone(self):
        self.assertEqual("z_1", self.zone_1.name)
        self.assertEqual("z_1", self.zone_2.parent_zone_name)

    # @unittest.skip
    def test_show(self):
        ZoneHelper.show(self.zone_1)
        ZoneHelper.show(self.zone_2)

    # def test_max_delay_error_0(self):
    #     try:
    #         self.seg_1.max_delay = 0
    #     except TypeError:
    #         pass
    #     else:
    #         self.fail("The max_delay must be greater than 0, was not detected")
    #
    # def test_max_delay_error_minus_one(self):
    #     try:
    #         self.seg_1.max_delay = -1
    #     except TypeError:
    #         pass
    #     else:
    #         self.fail("The max_delay must be greater than 0, was not detected")

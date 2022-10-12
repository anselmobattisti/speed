# import os
# import unittest
#
# from SimPlacement.setup import Setup
# from SPED.entities.zone import Zone
# from SPED.helpers.zone import ZoneHelper
#
#
# class SPEDTest(unittest.TestCase):
#
#     entities_file = "{}/config/entities_topology_build.yml".format(os.path.dirname(os.path.abspath(__file__)))
#     log_path = "{}/logs".format(os.path.dirname(os.path.abspath(__file__)))
#     environment = None
#
#     def test_create_zone(self):
#         self.assertEqual("z_1", self.zone_1.name)
#         self.assertEqual("z_1", self.zone_2.parent_zone_name)
#
#     # @unittest.skip
#     def test_show(self):
#         ZoneHelper.show(self.zone_1)
#         ZoneHelper.show(self.zone_2)
#
#     # def test_max_delay_error_0(self):
#     #     try:
#     #         self.seg_1.max_delay = 0
#     #     except TypeError:
#     #         pass
#     #     else:
#     #         self.fail("The max_delay must be greater than 0, was not detected")
#     #
#     # def test_max_delay_error_minus_one(self):
#     #     try:
#     #         self.seg_1.max_delay = -1
#     #     except TypeError:
#     #         pass
#     #     else:
#     #         self.fail("The max_delay must be greater than 0, was not detected")

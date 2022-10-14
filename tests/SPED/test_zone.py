import os
import unittest
from typing import Dict

from SimPlacement.setup import Setup
from SPED.entities.zone import Zone
from SPED.entities.sped import SPED
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
        nodes = cls.environment['nodes']

        sped_1 = SPED(
            name='sped_1',
            domain=domains['dom_1'],
            node=nodes['n_1'],
            zone_name="z_1",
        )

        sped_2 = SPED(
            name='sped_2',
            domain=domains['dom_2'],
            node=nodes['n_4'],
            zone_name="z_2",
        )

        cls.zone_1 = Zone(
            name="z_1",
            zone_type=Zone.TYPE_AGGREGATION,
            sped=sped_1,
            child_zone_names=["z_2", "z_3"],
        )

        cls.zone_2 = Zone(
            name="z_2",
            zone_type=Zone.TYPE_COMPUTE,
            sped=sped_2,
            child_zone_names=[],
            parent_zone_name="z_1"
        )

    def test_create_zone(self):
        self.assertEqual("z_1", self.zone_1.name)
        self.assertEqual("z_1", self.zone_2.parent_zone_name)

    def test_build_zones_from_file(self):
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

        # for zone_name, zone in zones.items():
        #     ZoneHelper.show(zone)

        self.assertEqual("aggregation", zones['z_1'].zone_type)
        self.assertEqual("z_1", zones['z_1'].name)
        self.assertEqual(2, len(zones['z_2'].child_zone_names))
        self.assertEqual("z_3", zones['z_8'].parent_zone_name)
        self.assertEqual("dom_4", zones['z_7'].sped.domain.name)

        img_file = "{}/img/zone_topology.png".format(os.path.dirname(os.path.abspath(__file__)))
        ZoneHelper.save_image(
            zones=zones,
            title="Generated Zones",
            file_name=img_file,
            img_width=15,
            img_height=15
        )

        # topology = environment['topology']
        # img_t_file = "{}/img/zone_hierarch.png".format(os.path.dirname(os.path.abspath(__file__)))
        # topology.save_image(
        #     topology.get_graph(),
        #     "Full Topology",
        #     img_t_file
        # )

    # # @unittest.skip
    # def test_show(self):
    #     ZoneHelper.show(self.zone_1)
    #     ZoneHelper.show(self.zone_2)

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

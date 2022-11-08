import os
import os.path

import unittest
from typing import Dict

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

        cls.zone_1 = Zone(
            name="z_1",
            zone_type=Zone.TYPE_AGGREGATION,
            child_zone_names=["z_2", "z_3"],
        )

        cls.zone_2 = Zone(
            name="z_2",
            zone_type=Zone.TYPE_COMPUTE,
            child_zone_names=[],
            parent_zone_name="z_1"
        )

    def test_create_zone(self):
        self.assertEqual("z_1", self.zone_1.name)
        self.assertEqual("z_1", self.zone_2.parent_zone_name)

    def test_build_zones_from_file(self):
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

        self.assertEqual("aggregation", zones['z_1'].zone_type)
        self.assertEqual("z_1", zones['z_1'].name)
        self.assertEqual(2, len(zones['z_2'].child_zone_names))
        self.assertEqual("z_3", zones['z_8'].parent_zone_name)
        self.assertEqual("dom_5", zones['z_8'].domain_name)

    def test_build_zones_from_file_4_levels(self):
        """
        Build the zone topology with 4 levels
        """
        entities_file = "{}/config/entities_topology_build.yml".format(os.path.dirname(os.path.abspath(__file__)))
        zone_file = "{}/config/zone_topology_3.yml".format(os.path.dirname(os.path.abspath(__file__)))

        environment = Setup.load_entities(entities_file)

        zones: Dict[str, Zone] = ZoneHelper.load(
            data_file=zone_file,
            environment=environment
        )

        self.assertEqual("aggregation", zones['z_1'].zone_type)

    def test_build_save_image(self):
        """
        Build the zone topology from the data loaded from the config file.
        """
        entities_file = "{}/config/entities_topology_build.yml".format(os.path.dirname(os.path.abspath(__file__)))
        zone_file = "{}/config/zone_topology_2.yml".format(os.path.dirname(os.path.abspath(__file__)))

        environment = Setup.load_entities(entities_file)

        zones: Dict[str, Zone] = ZoneHelper.load(
            data_file=zone_file,
            environment=environment
        )

        img_file = "{}/img/zone_topology_2.png".format(os.path.dirname(os.path.abspath(__file__)))
        ZoneHelper.save_image(
            zones=zones,
            title="Zones Topology 2",
            file_name=img_file,
            img_width=15,
            img_height=15
        )

        self.assertTrue(os.path.isfile(img_file))

        # remove the created file.
        os.remove(img_file)

    def test_zone_names(self):
        """
        Get all the name based on a type
        """
        entities_file = "{}/config/entities_topology_build.yml".format(os.path.dirname(os.path.abspath(__file__)))
        zone_file = "{}/config/zone_topology.yml".format(os.path.dirname(os.path.abspath(__file__)))

        environment = Setup.load_entities(entities_file)

        zones: Dict[str, Zone] = ZoneHelper.load(
            data_file=zone_file,
            environment=environment
        )

        compute_zone_names = ZoneHelper.get_zone_names(
            zones=zones
        )

        aggregation_zone_names = ZoneHelper.get_zone_names(
            zones=zones,
            zone_type=Zone.TYPE_AGGREGATION
        )

        self.assertEqual(['z_4', 'z_5', 'z_6', 'z_7', 'z_8'], compute_zone_names)
        self.assertEqual(['z_1', 'z_2', 'z_3'], aggregation_zone_names)

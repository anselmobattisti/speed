import pandas as pd

import os
import unittest

from SimPlacement.setup import Setup
from SPEED.logs.vnf_segment import VNFSegmentLog


class SPEEDLogTest(unittest.TestCase):

    entities_file = "{}/config/entities.yml".format(os.path.dirname(os.path.abspath(__file__)))
    log_path = "{}/logs".format(os.path.dirname(os.path.abspath(__file__)))

    def test_create_segment(self):
        environment = Setup.load_entities(self.entities_file)

        segment_log: VNFSegmentLog = VNFSegmentLog()
        vnfs = environment['vnfs']

        segment_log.add_event(
            event=VNFSegmentLog.CREATED,
            time=0,
            sfc_request_name="sr_1",
            zone_name="zn_1",
            vnf_names=['vnf_1', 'vnf_3']
        )

        segment_log.add_event(
            event=VNFSegmentLog.CREATED,
            time=0,
            sfc_request_name="sr_2",
            zone_name="zn_1",
            vnf_names=['vnf_2', 'vnf_3']
        )

        segment_log.save(file_path=self.log_path)

        f = "{}/{}".format(self.log_path, VNFSegmentLog.FILE_NAME)
        df = pd.read_csv(f)
        self.assertEqual(2, df.size)

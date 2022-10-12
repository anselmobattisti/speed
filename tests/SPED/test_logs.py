import pandas as pd

import os
import unittest

from SimPlacement.setup import Setup
from SPED.logs.vnf_segment import VNFSegmentLog


class SPEDLogTest(unittest.TestCase):

    entities_file = "{}/config/entities.yml".format(os.path.dirname(os.path.abspath(__file__)))
    log_path = "{}/logs".format(os.path.dirname(os.path.abspath(__file__)))

    def test_create_segment(self):
        environment = Setup.load_entities(self.entities_file)

        segment_log: VNFSegmentLog = VNFSegmentLog()
        vnfs = environment['vnfs']

        segment_log.add_event(
            event=VNFSegmentLog.CREATED,
            time=0,
            segment_name="seg_1",
            vnfs=[vnfs['vnf_1'], vnfs['vnf_3']]
        )

        segment_log.add_event(
            event=VNFSegmentLog.CREATED,
            time=0,
            segment_name="seg_2",
            vnfs=[vnfs['vnf_2'], vnfs['vnf_3']]
        )

        segment_log.save(file_path=self.log_path)

        f = "{}/{}".format(self.log_path, VNFSegmentLog.FILE_NAME)
        df = pd.read_csv(f)
        self.assertEqual(2, df.size)

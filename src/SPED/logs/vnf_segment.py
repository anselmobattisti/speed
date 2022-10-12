import csv
import os
from typing import List

import pandas as pd

from SimPlacement.logs.log import Log
from SimPlacement.entities.vnf import VNF


class VNFSegmentLog(Log):
    """
    This class manages the Segments logs.
    """
    NAME = "segment"

    COLUMNS = ["Event", "Time", "Segment", "VNFs"]
    """
    The column title of the CSV file.
    """

    FILE_NAME = "segment.csv"
    """
    Name of the CSV file.
    """

    CREATED = "SEGMENT_CREATED"
    """
    Caused when the segment is created.
    """

    def __init__(self):
        """
        Segment logs.
        """
        self.events = list()

    def add_event(self, event: str, time: int, segment_name: str, vnfs: List[VNF]):
        """
        Add a new event.


        :param event: The name of the event.
        :param time: Time of the event.
        :param vnfs: The list with the VNFs.
        :param segment_name: The name of the segment.

        :return:
        """
        vnfs_name = []
        for aux_vnf in vnfs:
            vnfs_name.append(aux_vnf.name)

        log = [
            event,
            "{:.2f}".format(time),
            segment_name,
            ", ".join(vnfs_name)
        ]
        self.events.insert(0, log)

    def save(self, file_path="."):
        """
        Save the events.

        :param file_path: The path where the log file will be created.
        """
        if not os.path.exists(file_path):
            os.makedirs(file_path)  # pragma: no cover

        file_name = "{}/{}".format(file_path, self.FILE_NAME)
        df = self.flush(pd.DataFrame(columns=self.COLUMNS), self.events)
        df.to_csv(file_name, sep=';', index=False, quoting=csv.QUOTE_NONE)

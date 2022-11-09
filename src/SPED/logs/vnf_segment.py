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

    COLUMNS = ["Event", "Time", "SFC_Request_Name", "Zone", "VNFs"]
    """
    The column title of the CSV file.
    """

    FILE_NAME = "segment.csv"
    """
    Name of the CSV file.
    """

    CREATED = "CREATED"
    """
    Caused when the segment is created.
    """

    COMPUTE_ZONE_SELECTED = "COMPUTE_ZONE_SELECTED"
    """
    Caused when the compute zone is selected.
    """

    AGGREGATION_ZONE_SELECTED = "AGGREGATION_ZONE_SELECTED"
    """
    Caused when the aggregation zone is selected.
    """

    def __init__(self):
        """
        Segment logs.
        """
        self.events = list()

    def add_event(self, event: str, time: int, sfc_request_name: str, zone_name: str, vnf_names: List):
        """
        Add a new event.

        :param event: The name of the event.
        :param time: Time of the event.
        :param sfc_request_name: The name of the SFC Requested.
        :param zone_name: The name of the Zone.
        :param vnf_names: The list with the VNFs.

        :return:
        """

        log = [
            event,
            "{:.2f}".format(time),
            sfc_request_name,
            zone_name,
            ", ".join(vnf_names)
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

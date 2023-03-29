import csv
import os
from typing import List

import pandas as pd

from SimPlacement.logs.log import Log
from SimPlacement.entities.vnf import VNF


class DataAggregationLog(Log):
    """
    This class manages the Segments logs.
    """
    NAME = "data_aggregation"

    COLUMNS = ["Event", "Time", "Zone", "Size"]
    """
    The column title of the CSV file.
    """

    FILE_NAME = "data_aggregation.csv"
    """
    Name of the CSV file.
    """

    COMPUTED = "COMPUTED"
    """
    Caused when the data aggregation is computed.
    """

    def __init__(self):
        """
        Segment logs.
        """
        self.events = list()

    def add_event(self, event: str, time: int, zone_name: str, size: int):
        """
        Add a new event.

        :param event: The name of the event.
        :param time: Time of the event.
        :param zone_name: The name of the Zone.
        :param size: The data aggregation size.

        :return:
        """

        log = [
            event,
            "{:.2f}".format(time),
            zone_name,
            size
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

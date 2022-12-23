import csv
import os
import pandas as pd

from SimPlacement.logs.log import Log


class DistributedPlacementLog(Log):
    """
    This class manages the Segments logs.
    """
    NAME = "distributed_placement"

    COLUMNS = ["Event", "Time", "SFC_Request_Name", "Cost"]
    """
    The column title of the CSV file.
    """

    FILE_NAME = "distributed_placement.csv"
    """
    Name of the CSV file.
    """

    SUCCESS = "SUCCESS"
    """
    Caused when the distributed service is placed.
    """

    FAIL = "FAIL"
    """
    Caused when the distributed service is NOT placed.
    """

    def __init__(self):
        """
        Distributed Service Placement logs.
        """
        self.events = list()

    def add_event(self, event: str, time: int, sfc_request_name: str, cost: float = 0):
        """
        Add a new event.

        :param cost: The cost of the placement.
        :param event: The name of the event.
        :param time: Time of the event.
        :param sfc_request_name: The name of the SFC Requested.

        :return:
        """

        log = [
            event,
            "{:.2f}".format(time),
            sfc_request_name,
            cost
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

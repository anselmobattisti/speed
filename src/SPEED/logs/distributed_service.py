import csv
import os
import pandas as pd

from SimPlacement.logs.log import Log


class DistributedServiceLog(Log):
    """
    This class manages the Segments logs.
    """
    NAME = "distributed_service"

    COLUMNS = ["Event", "Time", "SFC_Request_Name", "Zone_Manager"]
    """
    The column title of the CSV file.
    """

    FILE_NAME = "distributed_service.csv"
    """
    Name of the CSV file.
    """

    CREATED = "CREATED"
    """
    Caused when the distributed service is created.
    """

    FAIL = "FAIL"
    """
    Caused when the distributed service fails during the distributed placement process.
    """

    COMPUTE_ZONE_NO_RESOURCE = "COMPUTE_ZONE_NO_RESOURCE"
    """
    Caused when the compute zone selected to execute a VNF Instance does not have the resource anymore.
    """

    PLACED = "PLACED"
    """
    Caused when all the VNFs were placed.
    """

    VNFs_ASSIGNED_TO_COMPUTE_ZONE = "VNFs_ASSIGNED_TO_COMPUTE_ZONE"
    """
    Caused when all the VNFs were assigned to a compute zone.
    """

    TIMEOUT = "TIMEOUT"
    """
    Caused when all the distributed placements takes too long.
    """

    ZONE_MANAGER_SELECTED = "ZONE_MANAGER_SELECTED"
    """
    Caused when the ZONE MANAGER TO A requested services is selected.
    """

    NO_SEGMENTATION_PLANS = "NO_SEGMENTATION_PLANS"
    """
    Caused when the creation of the segmentation plan fails.
    """

    def __init__(self):
        """
        Distributed Service logs.
        """
        self.events = list()

    def add_event(self, event: str, time: int, sfc_request_name: str, zone_manager_name: str):
        """
        Add a new event.

        :param event: The name of the event.
        :param time: Time of the event.
        :param sfc_request_name: The name of the SFC Requested.
        :param zone_manager_name: The name of the Zone.

        :return:
        """

        log = [
            event,
            "{:.2f}".format(time),
            sfc_request_name,
            zone_manager_name
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

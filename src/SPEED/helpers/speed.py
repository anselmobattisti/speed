from typing import List

from SimPlacement.helper import Helper
from beautifultable import BeautifulTable
from komby.komby import Komby

from SPEED.types import InfrastructureData
from SPEED.types import AggregatedData


class SPEEDHelper(Helper):

    @staticmethod
    def vnf_segmentation(vnf_names: List[str]) -> dict:
        """
        Create the VNF Segmentations plan

        :param vnf_names: List of the vnf names
        :return: :dict
        """
        segmentation_plans = Komby.partitions(vnf_names)

        plans = dict()
        count_plan = 0
        for plan in segmentation_plans:
            plan_name = "plan_{}".format(count_plan)
            plans[plan_name] = dict()
            segments = dict()
            count_segments = 0
            for segment in plan:
                segment_name = "seg_{}".format(count_segments)
                segments[segment_name] = dict()
                segments[segment_name]["vnfs"] = segment
                segments[segment_name]["zones"] = []
                count_segments += 1
            count_plan += 1

            plans[plan_name]['segments'] = segments

        return plans

    @staticmethod
    def show_infrastructure_data(infrastructure_data: InfrastructureData):  # pragma: no cover
        """
        Print the infrastructure data.

        :param infrastructure_data: The Infrastructure Data object.
        :return:
        """
        if not type(infrastructure_data) == dict:
            raise TypeError("The data must be a InfrastructureData object.")

        table = BeautifulTable()

        zone: str
        vnf: str
        gw: str
        delay: int
        node: str
        cost: float
        cpu_available: int
        mem_available: int

        table.rows.append([infrastructure_data['zone']])
        table.rows.append([infrastructure_data['node']])
        table.rows.append([infrastructure_data['vnf']])
        table.rows.append([infrastructure_data['gw']])
        table.rows.append([infrastructure_data['delay']])
        table.rows.append([infrastructure_data['cost']])
        table.rows.append([infrastructure_data['cpu_available']])
        table.rows.append([infrastructure_data['mem_available']])

        table.rows.header = [
            "Zone",
            "Node",
            "VNF",
            "GW",
            "Delay",
            "Cost",
            "CPU Available",
            "MEM Available"
        ]

        print("\n")
        print(table)

    @staticmethod
    def show_aggregated_data(aggregated_data: AggregatedData):  # pragma: no cover
        """
        Print the aggregated zone.

        :param aggregated_data: The Aggregated data object.
        :return:
        """
        if not type(aggregated_data) == dict:
            raise TypeError("The data must be a AggregatedData object.")

        table = BeautifulTable()

        table.rows.append([aggregated_data['zone']])
        table.rows.append([aggregated_data['vnf']])
        table.rows.append([aggregated_data['gw']])
        table.rows.append([aggregated_data['delay']])
        table.rows.append([aggregated_data['cost']])

        table.rows.header = [
            "Zone",
            "VNF",
            "GW",
            "Delay",
            "Cost"
        ]

        print("\n")
        print(table)

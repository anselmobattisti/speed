from typing import List, Dict

from SimPlacement.entity import Entity
from SimPlacement.entities.domain import Domain
from SimPlacement.entities.node import Node
from SPED.types import InfrastructureData
from SPED.types import AggregatedData
from SPED.helpers.sped import SPEDHelper


class SPED(Entity):
    """
    This class represent the SPED component.
    """

    def __init__(self, name: str, node: Node, zone_name: str, domain: Domain = None, extra_parameters: dict = None):
        """
        Create the SPED component.

        :param name: The name of the SPED component.
        :param domain: The domain where the SPED is executed.
        :param node: The node where the SPED is executed.
        :param zone_name: The name of the zone where the SPED is connected.
        :param extra_parameters: Dict with extra parameters.
        """
        super().__init__(name, extra_parameters)
        self.domain = domain
        self.node = node
        self.zone_name = zone_name

        aux_data = None
        if self.domain:
            aux_data = self.compute_zone_data_collect()

        # local domain
        self.infrastructure_data: List[InfrastructureData] = aux_data
        self.aggregated_infrastructure_data: Dict[str, AggregatedData] = dict()

        # local + child domain aggregated data
        self.aggregated_data: Dict[str, AggregatedData] = dict()

    @property
    def domain(self):
        """
        The domain name.
        """
        return self._domain

    @domain.setter
    def domain(self, value: Domain):
        """
        Set the domain name.
        """
        if value and not type(value) == Domain:
            raise TypeError("The domain must be a Domain")

        self._domain = value

    @property
    def node(self):
        """
        The node where the SPED is executed.
        """
        return self._node

    @node.setter
    def node(self, value: str):
        """
        Set the node.
        """
        if value and not type(value) == Node:
            raise TypeError("The node must be a Node")

        self._node = value

    @property
    def zone_name(self):
        """
        The zone name.
        """
        return self._zone_name

    @zone_name.setter
    def zone_name(self, value: str):
        """
        Set the zone name.
        """
        if not type(value) == str:
            raise TypeError("The zone_name must be a str")

        self._zone_name = value

    def compute_zone_data_collect(self) -> List[InfrastructureData]:
        """
        Collect network and compute data about all the nodes in the zone domain:

            * Delay from each node to all the GWs.
            * The VNFs that can be executed in each node.

        :return: List with the data of the infrastructure
        """
        if not self.domain:
            raise TypeError("The zone {} must be compute zone".format(self.zone_name))

        infrastructure_data = []
        for node_name, node in self.domain.nodes.items():
            delay_to_all_gws = self.domain.delay_to_all_gws(node)
            for vnf_name, vnf in node.vnfs.items():
                if node.has_resources_to_execute_vnf(vnf):

                    cpu_cost = node.get_extra_parameter("cpu_cost")
                    mem_cost = node.get_extra_parameter("mem_cost")
                    cost = vnf.cpu * cpu_cost + vnf.mem * mem_cost

                    resource_available = node.resources_available()
                    for gw, delay in delay_to_all_gws.items():
                        aux_data = InfrastructureData(
                            zone=self.zone_name,
                            vnf=vnf_name,
                            gw=gw,
                            delay=delay,
                            node=node.name,
                            cost=cost,
                            cpu_available=resource_available['cpu'],
                            mem_available=resource_available['mem']
                        )
                        infrastructure_data.append(aux_data)

        self.infrastructure_data = infrastructure_data

        return infrastructure_data

    def aggregate_infrastructure_data(self) -> Dict[str, AggregatedData]:
        """
        Aggregate infrastructure data.

        Define the min cost to execute each VNFs to the WGW
        :return:
        """
        if not self.domain:
            raise TypeError("The zone {} must be compute zone".format(self.zone_name))

        aggregated_data: Dict[str, AggregatedData] = dict()

        infrastructure_data: List[InfrastructureData] = self.compute_zone_data_collect()

        for aux_data in infrastructure_data:
            key_name = "{}_{}".format(aux_data['gw'], aux_data['vnf'])
            if key_name not in aggregated_data.keys() or aggregated_data[key_name]['cost'] > aux_data['cost']:
                aggregated_data[key_name] = AggregatedData(
                    zone=aux_data['zone'],
                    vnf=aux_data['vnf'],
                    gw=aux_data['gw'],
                    delay=aux_data['delay'],
                    cost=aux_data['cost']
                )

        self.aggregated_infrastructure_data = aggregated_data

        return aggregated_data

    def update_aggregate_date(self, aggregated_infrastructure_data: Dict[str, AggregatedData]):
        """
        Update the aggregate_data with the data about all the child zones.

        :param aggregated_infrastructure_data:
        :return:
        """
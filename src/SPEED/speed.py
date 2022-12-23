import random
from typing import List, Dict
import networkx as nx
import sys

from SimPlacement.entity import Entity
from SimPlacement.entities.domain import Domain
from SimPlacement.entities.node import Node
from SPEED.types import InfrastructureData
from SPEED.types import AggregatedData


class SPEED(Entity):
    """
    This class represent the SPEED component.
    """

    def __init__(self, name: str, zone_name: str, domain: Domain = None,
                 environment: dict = None, extra_parameters: dict = None):
        """
        Create the SPEED component.

        :param name: The name of the SPEED component.
        :param zone_name: The name of the zone where the SPEED is connected.
        :param domain: The domain where the SPEED is executed.
        :param environment: The environment, its an auxiliar info about the environment where the zone is executed.
        :param extra_parameters: Dict with extra parameters.
        """

        super().__init__(name, extra_parameters)
        self.domain = domain
        self.zone_name = zone_name
        self.environment = environment
        aux_data = []
        # if self.domain:
        #     aux_data = self.compute_zone_data_collect()

        # local domain
        self.infrastructure_data: List[InfrastructureData] = aux_data
        self.aggregated_infrastructure_data: Dict[str, AggregatedData] = dict()

        # The data aggregated of the child zones
        self.child_zones_aggregated_data: Dict[str, Dict[str, AggregatedData]] = dict()

        # local + child zones aggregated data
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
            delay_to_all_gws = self.delay_to_all_gws(node)
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
            if key_name not in aggregated_data.keys() or aggregated_data[key_name]['delay'] > aux_data['delay']:
                aggregated_data[key_name] = AggregatedData(
                    zone=aux_data['zone'],
                    vnf=aux_data['vnf'],
                    gw=aux_data['gw'],
                    delay=aux_data['delay'],
                    cost=aux_data['cost']
                )

        self.aggregated_infrastructure_data = aggregated_data

        return aggregated_data

    def update_child_zone_aggregated_data(self, zone_name: str, child_zone_aggregated_data: Dict[str, AggregatedData]):
        """
        Add the aggregated data about a child zone in the parent zone.

        :param zone_name: The name of the child zone that send the data.
        :param child_zone_aggregated_data: The aggregated data in the child zone.
        :return:
        """
        # create a copy of each aggregated data and change the zone name to the child zone that send the data
        new_aggregated_data: Dict[str, AggregatedData] = dict()
        for aux_key, aux_data in child_zone_aggregated_data.items():
            new_aggregated_data[aux_key] = AggregatedData(
                zone=zone_name,
                vnf=aux_data['vnf'],
                gw=aux_data['gw'],
                delay=aux_data['delay'],
                cost=aux_data['cost']
            )

        self.child_zones_aggregated_data[zone_name] = new_aggregated_data

    def aggregate_date(self):
        """
        Process the local aggregated data, and the child received aggregated data and return to the parent zone.

        :return:
        """
        aggregated_data: Dict[str, AggregatedData] = dict()

        if self.domain:
            aggregated_data = self.aggregate_infrastructure_data()

        for aux_aggregated_data in self.child_zones_aggregated_data.values():
            for key_name, aux_data in aux_aggregated_data.items():
                if key_name not in aggregated_data.keys() or aggregated_data[key_name]['delay'] > aux_data['delay']:
                    aggregated_data[key_name] = aux_data

        self.aggregated_data = aggregated_data

        return aggregated_data

    def valid_segmentation_plans(self, plans: Dict) -> Dict:
        """
        Check the valid segmentation plan based on the zone data

        :param plans: The valid VNF Segmentations
        :return:
        """
        aux_plans = dict()
        vnf_in_zone: Dict[str, List[str]] = dict()

        for data in self.aggregated_data.values():
            if data['zone'] not in vnf_in_zone.keys():
                vnf_in_zone[data['zone']] = []

            if data['vnf'] not in vnf_in_zone[data['zone']]:
                vnf_in_zone[data['zone']].append(data['vnf'])

        for plan_name, aux_plan in plans.items():
            for zone_name, vnfs in vnf_in_zone.items():
                for segment_name, aux_segment in aux_plan['segments'].items():
                    valid = True
                    for vnf in aux_segment['vnfs']:
                        if vnf not in vnfs:
                            valid = False
                    if valid:
                        if zone_name not in aux_segment['zones']:
                            aux_segment['zones'].append(zone_name)

        for plan_name, aux_plan in plans.items():
            valid_plan = True
            for segment_name, aux_segment in aux_plan['segments'].items():
                if len(aux_segment['zones']) == 0:
                    valid_plan = False
            if valid_plan:
                aux_plans[plan_name] = aux_plan

        return aux_plans

    def delay_to_all_gws(self, node: Node) -> Dict[str, int]:
        """
        Return the delay from a node to all the GWs of the environment.

        :param node: The node.
        :return: Dict with the name of the GW as key, and the delay as value.
        """
        g = self.environment['topology'].get_graph()
        aux: Dict[str, int] = dict()
        nodes: Dict[str, Node] = self.environment['nodes']
        for node_name, aux_node in nodes.items():
            if aux_node.is_gateway():
                delay = nx.shortest_path_length(g, node.name, node_name, weight="delay")
                aux[node_name] = delay

        return aux

    def select_segmentation_plan(self, segmentation_plan: dict) -> dict:
        """
        Select the best segmentation plan to be processed.

        We select the plan with few VNF Segments.

        :param segmentation_plan:
        :return: dict
        """
        plans = list(segmentation_plan.keys())

        if not segmentation_plan:
            raise TypeError("The is no segmentation plan.")

        if len(plans) == 1:
            return segmentation_plan[plans[0]]

        min_size = sys.maxsize
        min_plans: List[dict] = []
        for plan in segmentation_plan.values():
            if min_size == len(plan['segments']):
                min_plans.append(plan)

            if min_size > len(plan['segments']):
                min_plans.clear()
                min_plans.append(plan)
                min_size = len(plan['segments'])

        selected_plan = random.choice(min_plans)

        return selected_plan

    def compute_child_zone_vnf_segment_execution_cost(self, vnf_segment: dict, zone_name: str) -> float:
        """
        Compute the cost for execute the segment in a child zone. The cost is computed based on the aggregated data
        stored in the parent zone.

        :param vnf_segment: VNFs in the segment
        :param zone_name: Name of the child zone
        :return:
        """
        cost = 0.0
        min_cost = dict()
        for vnf in vnf_segment['vnfs']:
            min_cost[vnf] = sys.maxsize
            for aggregated_data in self.aggregated_data.values():
                if aggregated_data['vnf'] == vnf and aggregated_data['zone'] == zone_name:
                    if min_cost[vnf] > aggregated_data['cost']:
                        min_cost[vnf] = aggregated_data['cost']

        for value in min_cost.values():
            cost = cost + float(value)

        return cost

    def vnfs_available(self):
        """
        Return a list with the VNFs available in the zone
        :return:
        """
        vnfs = dict()
        for data in self.aggregated_data.values():
            vnfs[data['vnf']] = 1

        for data in self.aggregated_infrastructure_data.values():
            vnfs[data['vnf']] = 1

        return list(vnfs.keys())

    def min_cost(self, vnf_name):
        """
        """
        costs = []
        for d in self.aggregated_data.values():
            if d['vnf'] == vnf_name:
                costs.append(d['cost'])

        return min(costs)
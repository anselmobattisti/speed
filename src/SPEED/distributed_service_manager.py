import random
from typing import Dict, List

from SPEED.entities.distributed_service import DistributedService
from SPEED.helpers.zone import ZoneHelper
from SPEED.speed import SPEED
from SPEED.entities.zone import Zone
from SimPlacement.entities.sfc_request import SFCRequest


class DistributedServiceManager:
    """
    The Service Manager (SM) has the following responsibilities:

    * Receive the SFC Request when its zone is the selected zone to coordinate the placement process.
    * Receive the VNFs that should be placed.
    * Create the VNF Segments.
    * Select the child zones that should execute each Segment.
    * After all VNF Segments finish the placed, this zone will terminate the process.

    Each zone have one SM that will deal with the services requested.
    """

    def __init__(self, zone: Zone, environment):
        """
        Create a new Slice Auction Manager.

        :param environment: The simulation environment.
        :param zone: The zone where the service manager is associated.
        """

        self.environment = environment
        """
        The environment simulation.
        """

        self.zone: Zone = zone
        """
        The zone which the auction manager is responsible.
        """
        domain = None

        if zone.domain_name:
            domain = environment['domains'][zone.domain_name]

        """
        The SPEED component.
        """
        self.speed: SPEED = SPEED(
                name='s_{}'.format(zone.name),
                domain=domain,
                zone_name=zone.name,
                environment=environment
            )

        self.node = ZoneHelper.get_random_node_from_zone(
            zone=zone,
            environment=environment
        )
        """
        Select one node from an above zone to be the node where the distributed service manager is executed
        Will be used during the simulation to find the delay until de child zones components.
        """

        self.sfc_requests: Dict[str, SFCRequest] = dict()
        """
        All the SFC Request which the zone is the manager.
        """

        self.distributed_services: Dict[str, DistributedService] = dict()
        """
        All the SFC Request which the zone is the manager.
        """

    def add_sfc_request(self, sfc_request: SFCRequest, placement_timeout: int) -> SFCRequest:
        """
        Add a new SFC Request that the zone will manager the distributed SFC Placement process.

        :param sfc_request: The SFC Request Object.
        :param placement_timeout: The max delay for the placement timeout.
        :return: SFCRequest
        """
        if sfc_request.name in self.sfc_requests.keys():
            raise TypeError("The SFC Request {} was already added.".format(sfc_request.name))

        self.distributed_services[sfc_request.name] = DistributedService(
            sfc_request=sfc_request,
            manager_zone=self.zone,
            placement_timeout=placement_timeout
        )

        self.sfc_requests[sfc_request.name] = sfc_request

        return self.sfc_requests[sfc_request.name]

    def add_segment_to_compute_zone(self, sfc_request: SFCRequest, vnf_names: List, zone: Zone):
        """
        The zone that will execute some VNF send this info to the zone manager of the requested service.

        :param sfc_request: The SFC Request.
        :param vnf_names: The list of the VNFs that will be execute in the zone.
        :param zone: The compute zone.

        :return:
        """
        # The SFC Request already enter in timeout
        if self.distributed_services[sfc_request.name].placement_timeout == 0:
            return False

        if sfc_request.name not in self.distributed_services.keys():
            raise TypeError("The Distributed Service {} not exist in the zone {}.".format(sfc_request.name,
                                                                                          self.zone.name))
        ds = self.distributed_services[sfc_request.name]

        for vnf_name in vnf_names:
            ds.add_vnf_to_zone(
                vnf_name=vnf_name,
                zone_name=zone.name
            )

        return True

    def select_zones_to_vnf_segments(self, segmentation_plan):
        """
        Select for each VNF Segment in the segmentation plan the zone that will execute the VNF Segment.

        :param segmentation_plan: The segmentation plan that will be processed in the zone
        :return:
        """
        vnf_segments = segmentation_plan['segments']
        selected_zone: Dict[str, str] = dict()
        for vnf_segment_name, vnf_segment in vnf_segments.items():
            zone_cost: Dict[str, float] = dict()
            for child_zone in self.zone.child_zone_names:
                zone_cost[child_zone] = self.speed.compute_child_zone_vnf_segment_execution_cost(
                    vnf_segment=vnf_segment,
                    zone_name=child_zone
                )

            if zone_cost:
                selected_zone[vnf_segment_name] = min(zone_cost, key=zone_cost.get)

        aux = dict()
        for vnf_segment, zone in selected_zone.items():
            aux[zone] = dict()
            aux[zone]['vnfs'] = vnf_segments[vnf_segment]['vnfs']

        return aux

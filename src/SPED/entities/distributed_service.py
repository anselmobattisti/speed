from typing import List

from SimPlacement.entities.sfc_request import SFCRequest
from SimPlacement.entities.virtual_link import VirtualLink
from SimPlacement.entity import Entity
from SPED.entities.vnf_segment import VNFSegment


class DistributedService(Entity):
    """
    The Distributed Service Entity.

    Each SFC Request after placed will generate a Distributed Service.
    """

    def __init__(self, name: str, sfc_request: SFCRequest, manager_zone_name: str, vnf_segments: List[VNFSegment],
                 ingress_link: VirtualLink = None, extra_parameters: dict = None):
        """
        Create a Distributed Service.

        :param name: The distributed service name.
        :param sfc_request: The SFC Request object.
        :param manager_zone_name: The name of the zone that manage the distributed service.
        :param vnf_segments: The list with the vnf_segments used to execute the SFC Requested.
        :param ingress_link: The virtual link from the src node of the SFC Request to the GW of the execution domain.
        :param extra_parameters: Dict with extra parameters.
        """
        super().__init__(name, extra_parameters)
        self.sfc_request = sfc_request
        self.manager_zone_name = manager_zone_name
        self.vnf_segments = vnf_segments
        self.ingress_link = ingress_link

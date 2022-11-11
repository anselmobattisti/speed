from typing import List, Dict

from SimPlacement.entities.sfc_request import SFCRequest
from SimPlacement.entity import Entity

from SPED.entities.zone import Zone


class DistributedService(Entity):
    """
    The Distributed Service Entity.

    Each SFC Request after placed will generate a Distributed Service.
    """

    def __init__(self, sfc_request: SFCRequest, manager_zone: Zone, extra_parameters: dict = None):
        """
        Create a Distributed Service.

        :param sfc_request: The SFC Request object.
        :param manager_zone: The zone that manages the distributed service.
        :param extra_parameters: Dict with extra parameters.
        """
        super().__init__(sfc_request.name, extra_parameters)
        self.sfc_request = sfc_request
        self.manager_zone = manager_zone
        self.vnf_zones = dict()
        self.placed = False

        # For each VNF in the request create the zone entry in the dict
        for aux_vnf in sfc_request.sfc.vnfs:
            self.vnf_zones[aux_vnf.name] = None

    def add_vnf_to_zone(self, vnf_name: str, zone_name: str):
        """
        Add the vnf to the compute zone.

        :param vnf_name: The name of the VNF.
        :param zone_name: The name of the Zone.

        :return:
        """
        if self.vnf_zones[vnf_name]:
            raise TypeError("The VNF {} is already place in the zone zone {}.".format(vnf_name, zone_name))

        self.vnf_zones[vnf_name] = zone_name

    def check_if_placed(self) -> bool:
        """
        If all the VNFs of the requested SFC were assigned to a compute zone return True

        :return: True if all the VNFs were placed, False otherwise.
        """
        placed = True

        for zone in self.vnf_zones.values():
            if not zone:
                placed = False
                break

        if placed:
            self.placed = True

        return self.placed

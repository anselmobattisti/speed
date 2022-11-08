from typing import Dict, List
from beautifultable import BeautifulTable

from SimPlacement.helper import Helper
from SPED.entities.zone import Zone
from SimPlacement.entities.sfc_request import SFCRequest


class DistributedServiceHelper(Helper):

    @staticmethod
    def get_vnf_names_from_sfc_request(sfc_request: SFCRequest) -> List:
        """
        Return a list with the names of the VNFs in the SFC requested.

        :param sfc_request: The SFC Request object.
        :return:
        """
        vnf_names = []

        for aux_vnf in sfc_request.sfc.vnfs:
            vnf_names.append(aux_vnf.name)

        return vnf_names

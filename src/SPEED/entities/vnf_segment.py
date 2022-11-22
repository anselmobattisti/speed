from typing import List

from SimPlacement.entity import Entity
from SimPlacement.entities.vnf import VNF
from SimPlacement.entities.domain import Domain


class VNFSegment(Entity):
    """
    This class represent the abstraction of a VNF Segment.

    One VNF Segment encompasses one or more VNFs. All the VNFs inside a VNF Segment will be placed in the same Zone.
    """

    def __init__(self, name: str, vnfs: List[VNF], max_delay: int, extra_parameters: dict = None):
        """
        Create a VNF Segment.

        :param name: The name of the VNF.
        :param vnfs: The list of VNFs encompassed by the VNF Segment.
        :param max_delay: The delay tolerable by the SFC.
        :param extra_parameters: Dict with extra parameters.
        """
        super().__init__(name, extra_parameters)
        self.vnfs = vnfs
        self.max_delay = max_delay
        self.domain = None
        """
        The domain where the VNFs of the VNF Segment are executed.
        """

    @property
    def vnfs(self):
        """
        List of VNFs that compose the VNF Segment.
        """
        return self._vnfs

    @vnfs.setter
    def vnfs(self, value: List[VNF]):
        """
        Define the list of VNFs that compose the VNF Segment.
        """
        if value and not type(value) == list:
            raise TypeError("The vnfs must be a list of VNFs.")

        self._vnfs = value

    @property
    def max_delay(self):
        """
        The max delay tolerable by the VNF Segment. The sum of all link delay used to bind the VNFs.
        """
        return self._max_delay

    @max_delay.setter
    def max_delay(self, value):
        """
        Set the max_delay.
        """
        if value <= 0:
            raise TypeError("The max_delay must be greater than 0.")

        self._max_delay = value

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

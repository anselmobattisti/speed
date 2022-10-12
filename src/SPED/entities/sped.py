from SimPlacement.entity import Entity
from SimPlacement.entities.domain import Domain
from SimPlacement.entities.node import Node


class SPED(Entity):
    """
    This class represent the SPED component.
    """

    def __init__(self, name: str, domain: Domain, node: Node, zone_name: str, extra_parameters: dict = None):
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
        if not type(value) == Domain:
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
        if not type(value) == Node:
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
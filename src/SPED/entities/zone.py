from typing import List

from SimPlacement.entity import Entity
from SPED.entities.sped import SPED


class Zone(Entity):
    """
    This class represent the abstraction of a zone.
    """

    TYPE_COMPUTE = "compute"
    """
    Constant used to define zones that provides computational resources for VNF Instances execution.
    """

    TYPE_AGGREGATION = "aggregation"
    """
    Constant used to define zones that aggregate other zones data informations.
    """

    TYPE_ACCESS = "access"
    """
    Constant used to define nodes where the user is connected.
    """

    VALID_TYPES = [TYPE_COMPUTE, TYPE_AGGREGATION, TYPE_ACCESS]
    """
    Constant used to define zone valid types.
    """

    def __init__(self, name: str, zone_type: str, sped: SPED, child_zone_names=List[str],
                 parent_zone_name: str = None, extra_parameters: dict = None):
        """
        Create a Zone.

        :param name: The name of the Zone.
        :param zone_type: The zone_type.
        :param sped: The SPED component.
        :param child_zone_names: The list of child zones name.
        :param parent_zone_name: The name of the parent zone.
        :param extra_parameters: Dict with extra parameters.
        """
        super().__init__(name, extra_parameters)
        self.zone_type = zone_type
        self.sped: SPED = sped
        self.child_zone_names = child_zone_names
        self.parent_zone_name = None

        if parent_zone_name:
            self.parent_zone_name = parent_zone_name

    @property
    def zone_type(self):
        """
        The zone type.
        """
        return self._zone_type

    @zone_type.setter
    def zone_type(self, value: str):
        """
        Set the zone type.
        """
        if not type(value) == str:
            raise TypeError("The zone_type must be a string")

        if value not in Zone.VALID_TYPES:
            raise TypeError("The zone_type is invalid")

        self._zone_type = value

    @property
    def sped(self) -> SPED:
        """
        The SPED component.
        """
        return self._sped

    @sped.setter
    def sped(self, value: SPED):
        """
        Set the SPED component.
        """
        if not type(value) == SPED:
            raise TypeError("The sped must be a SPED")

        self._sped = value

    @property
    def child_zone_names(self):
        """
        List of the name of child zones.
        """
        return self._child_zone_names

    @child_zone_names.setter
    def child_zone_names(self, value: List[str]):
        """
        Define the name of child zones.
        """
        if not type(value) == list:
            raise TypeError("The vnfs must be a list of str.")

        self._child_zone_names = value

    @property
    def parent_zone_name(self):
        """
        The entity parent zone.
        """
        return self._parent_zone_name

    @parent_zone_name.setter
    def parent_zone_name(self, value: str):
        """
        Set the entity parent zone name.
        """
        if value and not type(value) == str:
            raise TypeError("The parent_zone_name must be a string")

        self._parent_zone_name = value

    def add_child_zone_name(self, value: str):
        """
        Add a child zone name to the zone
        """
        self.child_zone_names.append(value)

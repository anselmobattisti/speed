from beautifultable import BeautifulTable

from SimPlacement.helper import Helper
from SPED.entities.zone import Zone


class ZoneHelper(Helper):

    @staticmethod
    def show(zone: Zone):  # pragma: no cover
        """
        Print the Zone.

        :param zone: The Zone object.
        :return:
        """
        if not type(zone) == Zone:
            raise TypeError("The zone must be a Zone object.")

        table = BeautifulTable()

        table.rows.append([zone.name])
        table.rows.append([zone.domain.name])
        table.rows.append([zone.parent_zone_name])
        table.rows.append([", ".join(zone.child_zone_names)])

        table.rows.header = [
            "Zone",
            "Domain",
            "Parent",
            "Child's",
        ]

        print("\n")
        print(table)

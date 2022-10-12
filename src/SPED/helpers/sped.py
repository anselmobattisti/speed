# import yaml
#
# from SimPlacement.helper import Helper
# from beautifultable import BeautifulTable
#
#
# class SPEDHelper(Helper):
#
#     @staticmethod
#     def build_zone_topology(domains):
#         """
#         Build the zone topology based on the domains configured.
#
#         :param domains: the loaded domains.
#         :return: Dict with all the UEs.
#         """
#         attrs = Helper.get_attributes(vars(UE))
#         data = UEHelper.load_yml_file(data_file)
#
#         try:
#             ue_data = data["user_equipments"]
#         except KeyError:
#             raise TypeError("Config file does not have the field 'user_equipments'.")
#
#         ues = {}
#
#         for name, ue in ue_data.items():
#
#             # Verify if the attributes of the imported UE have all the required attributes.
#             if not Helper.validate_attributes(attrs, ue):
#                 raise TypeError("There are differences between the attributes in the UE Class and the imported file")
#
#             extra = None
#             if "extra_parameters" in ue:
#                 extra = ue["extra_parameters"]
#
#             aux = UE(
#                 name=name,
#                 ue_type=ue["type"],
#                 extra_parameters=extra
#             )
#
#             ues[name] = aux
#
#         return ues

import random

import networkx as nx
import numpy as np
import simpy

from typing import Dict, List

from SimPlacement.entities.node import Node
from SimPlacement.entities.packet import Packet
from SimPlacement.entities.sfc_request import SFCRequest
from SimPlacement.entities.virtual_link import VirtualLink
from SimPlacement.entities.vnf_instance import VNFInstance
from SimPlacement.helpers.packet import PacketHelper
from SimPlacement.log import SimLog
from SimPlacement.logs.sfc_instance import SFCInstanceLog
from SimPlacement.logs.virtual_link import VirtualLinkLog
from SimPlacement.sdn_controller import SDNController
from SimPlacement.topology import Topology
from SimPlacement.types import SFCPlacementPlan
from SimPlacement.logs.placement import PlacementLog
from SimPlacement.logs.packet import PacketLog
from SimPlacement.logs.vnf_instance import VNFInstanceLog
from SimPlacement.entities.domain import Domain
from SimPlacement.entities.sfc_instance import SFCInstance

from SPED.entities.distributed_service import DistributedService
from SPED.distributed_service_manager import DistributedServiceManager
from SPED.entities.zone import Zone
from SPED.helpers.zone import ZoneHelper
from SPED.helpers.sped import SPEDHelper
from SPED.helpers.distributed_service import DistributedServiceHelper
from SPED.logs.distributed_service import DistributedServiceLog
from SPED.logs.vnf_segment import VNFSegmentLog


class SPEDSimulation:
    """
    The simulation using the SPED Strategy to execute the distributed SFC Placement.
    """

    def __init__(self, env: simpy.Environment, config, environment):
        """
        The simulation component.

        :param env: SimPy environment.
        :param config: Simulation configuration parameters.
        :param environment: simulation environment.
        """

        if 'seed' in config.keys():
            random.seed(config['seed'])

        self.env = env
        """
        The SimPy environment object.
        """

        self.environment = environment
        """
        Dict with all the entities of the simulation.
        """

        self.config = config
        """
        Simulation config.
        """

        self.duration = config['duration']
        """
        The duration of the simulation.
        """

        self.vnf_instance_initial_status = config['vnf_instances']['initial_status']
        """
        Defines the VNF Instance status after its creation.
        """

        self.vnf_instance_ru_status = config['vnf_instances']['status_to_count_resource_usage']
        """
        List with the VNF Instance status that the resource used should be counted as reserved in the node.
        """

        self.sfc_requests: Dict[str, SFCRequest] = environment['sfc_requests']
        """
        Aux var with all the SFC Requests.
        """

        self.domains: Dict[str, Domain] = environment['domains']
        """
        Aux var with all the Domains.
        """

        self.zones: Dict[str, Zone] = environment['zones']
        """
        Aux var with all the Zones.
        """

        self.packets = environment['packets']
        """
        Aux var with all the packets.
        """

        self.log: SimLog = environment['log']
        """
        The log object store all the entities logs.
        """

        self.vnf_segment_log: VNFSegmentLog = VNFSegmentLog()
        self.log.register_log(name=VNFSegmentLog.NAME, log_obj=self.vnf_segment_log)
        """
        The object for logging the VNF Segments events.
        """

        self.distributed_service_log: DistributedServiceLog = DistributedServiceLog()
        self.log.register_log(name=DistributedServiceLog.NAME, log_obj=self.distributed_service_log)
        """
        The object for logging the Distributed Service Log events.
        """

        self.packet_log: PacketLog = self.log.get_log(SimLog.LOG_NAME_PACKET)
        """
        The object for logging the packet events.
        """

        self.placement_log: PlacementLog = self.log.get_log(SimLog.LOG_NAME_PLACEMENT)
        """
        The object for logging the placement events.
        """

        self.vnf_instance_log: VNFInstanceLog = self.log.get_log(SimLog.LOG_NAME_VNF_INSTANCE)
        """
        The object for logging the VNF Instance events.
        """

        self.virtual_link_log: VirtualLinkLog = self.log.get_log(SimLog.LOG_VIRTUAL_LINK)
        """
        The object for logging the virtual link events.
        """

        self.sfc_instance_log: SFCInstanceLog = self.log.get_log(SimLog.LOG_SFC_INSTANCE)
        """
        The object for logging the SFC Instance events.
        """

        # self.distributed_service_log = DistributedServiceLog()
        # self.log.register_log(DistributedServiceLog.NAME, self.distributed_service_log)
        # """
        # The object for logging the Distributed Services events.
        # """

        self.simpy_resource_vnf_instances: Dict[str, simpy.Resource] = dict()
        """
        Dict with the SimPy resources of the VNF Instances. Each VNF Instance will have one SimPy resource.
        """

        self.simpy_resource_virtual_links: Dict[str, simpy.Resource] = dict()
        """
        Dict with the SimPy resources of the Virtual Links. Each Virtual Link will have one SimPy resource.
        """

        self.packet_in_execution: Dict[str, List[Packet]] = dict(list())
        """
        All the packet that are in execution inside the simulation. The key is the name of the domain where the packet
        were created.
        """

        self.packet_delay_violated: Dict[str, List[Packet]] = dict(list())
        """
        All the packet that violated the max delay.
        """

        self.sdn_controller = SDNController(
            name="sdc_c",
            topology=environment['topology']
        )
        """
        Global SDN Controller that know all the Links and Nodes, only for the packet process. The placement componentes
        uses a SDN Controller only with the resources of the domain.
        """

        self.domain_zone: Dict[str, str] = dict()
        """
        Dictionary with the zone associated with the domain
        """

        self.zdsm: Dict[str, DistributedServiceManager] = dict()
        """
        Dictionary with the zone associated with each distributed service
        """

        self.sfc_request_zone_manager: Dict[str, Zone] = dict()
        """
        Dictionary with the zone associated with each sfc requested
        """

        self.graph_zones = ZoneHelper.build_zone_tree(self.zones)
        """
        Topology of the zones in a networkx Graph
        """

        self.default_placement_timeout = 100
        """
        The default value for the distributed service wait until set the placement as a fail.
        """

        self.setup()
        """
        Setup the initial configurations to execute the Auction Simulation.
        """

    def setup(self):
        """
        Configure the components to execute the distributed simulation.
        """

        if 'placement_timeout' in self.config.keys():
            self.default_placement_timeout = self.config['placement_timeout']

        for zone_name, zone in self.zones.items():
            if zone.zone_type == Zone.TYPE_ACCESS:
                continue

            if zone.domain_name:
                self.domain_zone[zone.domain_name] = zone_name

            # create one distributed service manager component for each zone.
            self.zdsm[zone_name] = DistributedServiceManager(
                zone=zone,
                environment=self.environment
            )

        for domain_name, domain in self.domains.items():
            self.packet_in_execution[domain_name] = list()
            self.packet_delay_violated[domain_name] = list()

            # The domain must have at least one gateway.
            has_gateway = False
            for aux_node_name, aux_node in domain.nodes.items():
                if aux_node.is_gateway():
                    has_gateway = True

            if not has_gateway:
                raise TypeError("The domain {} does not have any gateway node.".format(domain_name))

            # Configure the default cpu and memory cost for nodes without extra_parameters.
            for node_name, node in self.environment['nodes'].items():
                if 'node_cpu_default_cost' in self.config.keys():
                    node_cpu_default_cost = self.config['node_cpu_default_cost']
                else:
                    raise TypeError("The node_mem_default_cost is not defined in the simulation config file")

                if 'node_mem_default_cost' in self.config.keys():
                    node_mem_default_cost = self.config['node_mem_default_cost']
                else:
                    raise TypeError("The node_mem_default_cost is not defined in the simulation config file")

                if not node.extra_parameter_is_defined("cpu_cost"):
                    node.add_extra_parameter("cpu_cost", node_cpu_default_cost)

                if not node.extra_parameter_is_defined("mem_cost"):
                    node.add_extra_parameter("mem_cost", node_mem_default_cost)

            # Configure the default link cost for links without extra_parameters.
            for link_name, link in self.environment['links'].items():
                if 'link_default_cost' in self.config.keys():
                    link_default_cost = self.config['link_default_cost']
                else:
                    raise TypeError("The link_default_cost is not defined in the simulation config file")

                if not link.extra_parameter_is_defined("cost"):
                    link.add_extra_parameter("cost", link_default_cost)

    def run(self):
        """
        Execute the SimPy simulation process.

        :return: None
        """
        self.env.process(
            self.simulate()
        )
        """
        Add the main simulation process in the SimPy environment.
        """

        self.env.run(until=self.duration)
        """
        Run the simulation until the configured time limit (duration).
        """

        self.shutdown()
        """
        After the simulation flush the data and create the logs.
        """

    def simulate(self):
        """
        Execute the simulation main process.
        """

        while True:

            # Process the SFC Requests that arrived in the simulation time (env.now)
            if self.env.now in self.environment['sfc_requests_arrival']:
                sfc_requests = self.environment['sfc_requests_arrival'][self.env.now]

                # Execute the SPC Placement in a distributed fashion for each SFC Request.
                for sfc_request in sfc_requests:

                    # Update all the aggregated data in the simulation
                    self.update_aggregated_data()

                    try:

                        # Select the zone manager
                        aux = self.select_zone_manager(
                            sfc_request=sfc_request
                        )

                        zone_manager: Zone = aux['zone_manager']

                        vnf_names = DistributedServiceHelper.get_vnf_names_from_sfc_request(
                            sfc_request=sfc_request
                        )

                        # The zone that will manage this request
                        self.sfc_request_zone_manager[sfc_request.name] = zone_manager

                        placement_timeout = self.default_placement_timeout

                        if sfc_request.extra_parameter_is_defined('placement_timeout'):
                            placement_timeout = sfc_request.get_extra_parameter('placement_timeout')

                        self.zdsm[zone_manager.name].add_sfc_request(
                            sfc_request=sfc_request,
                            placement_timeout=placement_timeout
                        )

                        # Lot the selection zone will manage the SFC Request
                        self.distributed_service_log.add_event(
                            event=DistributedServiceLog.ZONE_MANAGER_SELECTED,
                            time=self.env.now,
                            sfc_request_name=sfc_request.name,
                            zone_manager_name=zone_manager.name
                        )

                    except TypeError:
                        # The requested service cannot be placed, there is no zone to manage this request.
                        self.distributed_service_log.add_event(
                            event=DistributedServiceLog.FAIL,
                            time=self.env.now,
                            sfc_request_name=sfc_request.name,
                            zone_manager_name="Not Found"
                        )
                        continue

                    # Zone manager executing the game
                    try:
                        self.env.process(
                            self.distributed_sfc_placement_process(
                                sfc_request=sfc_request,
                                zone=zone_manager,
                                vnf_names=vnf_names
                            )
                        )
                    except TypeError:
                        print("Simulation error")

            for i, domain in self.environment['domains'].items():
                self.dec_sfc_instances_timeout(domain)
                """
                Decrement the timeout of the SFC Instances.
                """

                self.inc_packet_delay(domain)
                """
                Increment the delay of the packet in execution.
                """

            # Iterate over the SFC Requests and log when the plan for placement arrives to the manager zone.
            self.sfc_requests_vnfs_are_assigned_to_compute_zone()

            # Do the simulation tick of 1ms
            yield self.env.timeout(1)

    def distributed_sfc_placement_process(self, sfc_request: SFCRequest, zone: Zone, vnf_names: List, timeout: int = 0):
        """
        Execute the game in each zone.

        :param sfc_request: The service requested
        :param zone: The zone where the game is executed
        :param vnf_names: The name of the VNFs.
        :param timeout: The delay between the distributed service component in the parent until the child
        zone component.

        :return:
        """

        yield self.env.timeout(timeout)

        # If the selected zone is a compute one, sent to the manager zone that the vnfs will be placed in that zone.
        if zone.zone_type == Zone.TYPE_COMPUTE:
            self.vnf_segment_log.add_event(
                event=VNFSegmentLog.COMPUTE_ZONE_SELECTED,
                time=self.env.now,
                sfc_request_name=sfc_request.name,
                zone_name=zone.name,
                vnf_names=vnf_names
            )

            zone_manager = self.sfc_request_zone_manager[sfc_request.name]
            ret = self.zdsm[zone_manager.name].add_segment_to_compute_zone(
                sfc_request=sfc_request,
                vnf_names=vnf_names,
                zone=zone
            )

            # The computed zone were selected after the timeout
            if not ret:
                self.vnf_segment_log.add_event(
                    event=VNFSegmentLog.TIMEOUT,
                    time=self.env.now,
                    sfc_request_name=sfc_request.name,
                    zone_name=zone.name,
                    vnf_names=vnf_names
                )
            return

        # If the selected zone is an aggregation zone it means that we need to execute the game again.
        if zone.zone_type == Zone.TYPE_AGGREGATION:
            # Log that the aggregation zone is selected to execute a set of VNFs
            self.vnf_segment_log.add_event(
                event=VNFSegmentLog.AGGREGATION_ZONE_SELECTED,
                time=self.env.now,
                sfc_request_name=sfc_request.name,
                zone_name=zone.name,
                vnf_names=vnf_names
            )

        # Run the distributed placement to the other zones
        dsm: DistributedServiceManager = self.zdsm[zone.name]

        plans = self.find_valid_vnf_segment_plan(
            zone=zone,
            vnf_names=vnf_names
        )

        selected_segmentation_plan = dsm.sped.select_segmentation_plan(plans)

        # This is the game implementation
        selected_child_zones = dsm.select_zones_to_vnf_segments(selected_segmentation_plan)

        for child_zone_name, vnfs in selected_child_zones.items():
            cz = self.zones[child_zone_name]

            timeout_to_child_zone = self.delay_between_distributed_service_components(
                zone_1=zone,
                zone_2=cz
            )

            # Send in parallel the request to place each VNF Segment.
            self.env.process(
                self.distributed_sfc_placement_process(
                    sfc_request=sfc_request,
                    zone=cz,
                    vnf_names=vnfs['vnfs'],
                    timeout=timeout_to_child_zone
                )
            )

        return

    def delay_between_distributed_service_components(self, zone_1: Zone, zone_2: Zone) -> int:
        """
        Return the delay between the distributed service components in two zones.

        :param zone_1: The first zone.
        :param zone_2: The second zone.
        :return:
        """
        topo: Topology = self.environment['topology']

        sp = topo.shortest_simple_edge_path(
            src_name=self.zdsm[zone_1.name].node.name,
            dst_name=self.zdsm[zone_2.name].node.name,
        )

        timeout = topo.path_delay(path=sp)

        return timeout

    def update_aggregated_data(self):
        """
        Update the aggregated data in all the zones. First the child zones will send the data to
        parent zone recursively.

        :return:
        """
        zones_to_update = nx.dfs_tree(self.graph_zones)
        list_zones = list(zones_to_update.nodes())

        # execute the update from the bottom to top
        list_zones.reverse()

        for zone_name in list_zones:
            zone = self.zones[zone_name]
            self.update_zone_aggregated_data(
                zone=zone
            )

    def update_zone_aggregated_data(self, zone: Zone):
        """
        Update the aggregated data for a zone.

        :return:
        """
        if zone.zone_type == Zone.TYPE_ACCESS:
            return

        dsm = self.zdsm[zone.name]

        # Aggregate the data from its own child zone
        aggregated_data = dsm.sped.aggregate_date()

        # Send data to the parent zone.
        if zone.parent_zone_name:
            self.zdsm[zone.parent_zone_name].sped.update_child_zone_aggregated_data(
                zone_name=zone.name,
                child_zone_aggregated_data=aggregated_data
            )

    def select_zone_manager(self, sfc_request: SFCRequest) -> dict:
        """
        Select the zone that manage the distributed placement process.

        The src and dst must be in one of the underlying zones.

        :param sfc_request: The SFC Request
        :return:
        """
        # Update the aggregated data for all the zones.
        self.update_aggregated_data()

        src_domain_name = self.domain_zone[sfc_request.src.domain_name]
        dst_domain_name = self.domain_zone[sfc_request.dst.domain_name]

        graph = self.graph_zones

        zone_manager_name = nx.lowest_common_ancestor(graph, src_domain_name, dst_domain_name)

        zone_manager: Zone = self.zones[zone_manager_name]

        vnf_names: List[str] = list()
        for vnf in sfc_request.sfc.vnfs:
            vnf_names.append(vnf.name)

        valid_zone_manager = False

        while True:
            valid_plans = self.find_valid_vnf_segment_plan(
                zone=zone_manager,
                vnf_names=vnf_names
            )

            if valid_plans:
                valid_zone_manager = True
                break

            if not valid_plans and not zone_manager.parent_zone_name:
                valid_zone_manager = False
                break

            if not valid_plans and zone_manager.parent_zone_name:
                zone_manager: Zone = self.zones[zone_manager.parent_zone_name]
                zone_manager_name = zone_manager.name

        if not valid_zone_manager:
            raise TypeError("The infrastructure can not execute the Service Requested {}.".format(sfc_request.name))

        return {
            'zone_manager': zone_manager,
            'plans': valid_plans
        }

    def find_valid_vnf_segment_plan(self, zone: Zone, vnf_names: List) -> dict:
        """
        Select the valid VNF Segments based on the zone where the game will be playerd.

        :param zone: The zone that will play the game.
        :param vnf_names: The list with the name of VNFs.
        :return:
        """
        # Update the aggregated data for all the zones.
        self.update_aggregated_data()

        segmentation_plans = SPEDHelper.vnf_segmentation(
            vnf_names=vnf_names
        )

        valid_plans = self.zdsm[zone.name].sped.valid_segmentation_plans(segmentation_plans)

        return valid_plans

    def execute_placement_plan(self, domain: Domain, plan: SFCPlacementPlan):
        """
        Execute the SFC Placement plan. Create the SFC Instance, VNF Instances and Virtual Links.

        :param domain: The domain object.
        :param plan: The SFC Placement plan.
        """
        # sdn_controller = domain.get_sdn_controller()
        sdn_controller = self.sdn_controller

        sfc_request: SFCRequest = self.sfc_requests[plan['sfc_request_name']]

        vnf_instances = domain.create_vnf_instance_from_placement_plan(
            plan=plan,
            initial_status=self.vnf_instance_initial_status,
            ru=self.vnf_instance_ru_status
        )

        """
        For each created VNF Instance, a simpy.Resource object will be created. SimPy use this object to control the
        access to the resource. For example, if a packet needs to be processed in the VNF Instance but already
        exist a packet being processed, thus the second packet must wait until the resource became free.
        """
        aux_vnf_instances: Dict[str, VNFInstance] = dict()
        for vnf_instance in vnf_instances:
            aux_vnf_instances[vnf_instance.vnf.name] = vnf_instance
            max_share = 1
            if vnf_instance.extra_parameter_is_defined("max_share"):
                max_share = vnf_instance.get_extra_parameter("max_share")

            self.simpy_resource_vnf_instances[vnf_instance.name] = simpy.Resource(self.env, capacity=max_share)

            # Create the log from VNF Instance creation.
            self.vnf_instance_log.add_event(
                event=VNFInstanceLog.CREATED,
                time=self.env.now,
                domain_name=domain.name,
                vnf_instance=vnf_instance
            )

        # Create the Virtual Links defined in the placement plan.
        aux_virtual_link: Dict[str, VirtualLink] = dict()
        for key, vnf in plan['vnfs'].items():
            vl_path = vnf['virtual_link_path']

            # It means that the next VNF is in the same node, thus a virtual link will not be necessary.
            if not vl_path:
                continue

            virtual_link = sdn_controller.create_virtual_link_from_path(
                path=vl_path,
                bw=sfc_request.sfc.required_bw
            )

            aux_virtual_link[key] = virtual_link

            self.virtual_link_log.add_event(
                event=VirtualLinkLog.CREATED,
                time=self.env.now,
                domain_name=domain.name,
                virtual_link=virtual_link
            )

            self.simpy_resource_virtual_links[virtual_link.name] = simpy.Resource(self.env)

        # Create the virtual link to the ingress node.
        ingress_link = None
        if plan['ingress_link_path']:
            ingress_link = sdn_controller.create_virtual_link_from_path(
                path=plan['ingress_link_path'],
                bw=sfc_request.sfc.required_bw
            )

            self.virtual_link_log.add_event(
                event=VirtualLinkLog.CREATED,
                time=self.env.now,
                domain_name=domain.name,
                virtual_link=ingress_link
            )

            self.simpy_resource_virtual_links[ingress_link.name] = simpy.Resource(self.env)

        sfc_instance = domain.create_sfc_instance(
            sfc_request=sfc_request,
            vnf_instances=aux_vnf_instances,
            virtual_links=aux_virtual_link,
            ingress_link=ingress_link
        )

        if sfc_instance:

            # Log the success in the placement plan creation.
            self.placement_log.add_event(
                event=PlacementLog.SUCCESS,
                time=self.env.now,
                domain_name=domain.name,
                sfc_request=sfc_request
            )

            self.sfc_instance_log.add_event(
                event=SFCInstanceLog.CREATED,
                time=self.env.now,
                domain_name=domain.name,
                sfc_instance=sfc_instance
            )
            return sfc_instance
        else:
            # Log the success in the placement plan creation.
            self.placement_log.add_event(
                event=PlacementLog.FAIL,
                time=self.env.now,
                domain_name=domain.name,
                sfc_request=sfc_request
            )

            raise TypeError("The SFC Instance could not be created.")

    def workload_process(self, distributed_service: DistributedService):
        """
        Start processing the packets (workload) of the SFC Request.

        :param distributed_service: The distributed service.
        """

        sfc_request_name = distributed_service.sfc_request.name

        packets: Dict[str, Packet] = self.packets[sfc_request_name]
        """
        All the packets of the SFC Request.
        """

        # In which time each packet must be processed. Multiple packets can arrive at same time.
        packets_time: Dict[int, List[Packet]] = PacketHelper.compute_packet_execution_time_based_on_simulation_time(
            packets=packets,
            time=self.env.now
        )

        # Run the packet workload
        while True:
            now = int(self.env.now)
            if now in packets_time.keys():
                packets_to_process = packets_time[now]
                for packet in packets_to_process:
                    # Packets will not wait to start being processed, thus the yield is unnecessary.
                    self.env.process(
                        self.process_packet(
                            packet=packet,
                            distributed_service=distributed_service
                        )
                    )

            # Execute the simulation tick of 1ms
            yield self.env.timeout(1)

    def process_packet(self, packet: Packet, distributed_service: DistributedService):
        """
        Process the packets over the ingress link, VNF Instances and Virtual Links.

        :param packet: The packet object.
        :param distributed_service: The Distributed Service.
        :return:
        """

        execution_domain: Domain = self.domains[distributed_service.execution_domain_name]

        sfc_instance = execution_domain.get_sfc_instance(
            sfc_request_name=distributed_service.sfc_request.name
        )

        sfc_request = distributed_service.sfc_request

        sfc_instance.reset_timeout()
        """
        A new packet to be processed will reset the SFC Instance timeout.
        """

        # Log the packet creation
        self.packet_log.add_event(
            event=PacketLog.CREATED,
            time=self.env.now,
            domain_name=sfc_request.src.domain_name,
            packet=packet
        )

        self.packet_in_execution[sfc_request.src.domain_name].append(packet)
        """
        Add the packet in the list of packet that are in execution
        """

        # Process the link the inter-domain link
        if distributed_service.ingress_link:
            yield self.env.process(
                self.process_packet_over_link(
                    packet=packet,
                    virtual_link=distributed_service.ingress_link,
                    domain=self.domains[sfc_request.src.domain_name]
                )
            )

        # If the SFC Instance have an ingress link thus process the packet over it.
        if sfc_instance.ingress_link:
            yield self.env.process(
                self.process_packet_over_link(
                    packet=packet,
                    virtual_link=sfc_instance.ingress_link,
                    domain=execution_domain
                )
            )

        for vnf in sfc_instance.sfc_request.sfc.vnfs:
            vnf_instance: VNFInstance = sfc_instance.vnf_instances[vnf.name]
            # Process the packet over the VNF Instance
            yield self.env.process(
                self.process_packet_over_vnf_instance(
                    packet=packet,
                    vnf_instance=vnf_instance,
                    domain=execution_domain
                )
            )

            # Only process the time in the virtual link if it exists.
            if vnf.name in sfc_instance.virtual_links.keys():
                virtual_link: VirtualLink = sfc_instance.virtual_links[vnf.name]
                # Process the packet over the Virtual Link
                yield self.env.process(
                    self.process_packet_over_link(
                        packet=packet,
                        virtual_link=virtual_link,
                        domain=execution_domain
                    )
                )

        # Process the link the inter-domain link
        if distributed_service.egress_link:
            yield self.env.process(
                self.process_packet_over_link(
                    packet=packet,
                    virtual_link=distributed_service.egress_link,
                    domain=self.domains[sfc_request.dst.domain_name]
                )
            )

        # Log that the packet was processed
        self.packet_log.add_event(
            event=PacketLog.PROCESSED,
            time=self.env.now,
            domain_name=sfc_request.dst.domain_name,
            packet=packet
        )

        self.packet_in_execution[sfc_request.src.domain_name].remove(packet)
        """
        Remove the packet from the list of packet that are in execution
        """

    def process_packet_over_vnf_instance(self, packet: Packet, vnf_instance: VNFInstance, domain: Domain):
        """
        Process the packet over the VNF Instance.

        :param packet: The packet object.
        :param vnf_instance: The VNF Instance object.
        :param domain: The domain object.
        :return:
        """
        domain_name = domain.name
        resource_vnf_instance = self.simpy_resource_vnf_instances[vnf_instance.name]

        self.packet_log.add_event(
            event=PacketLog.PACKET_VNF_INSTANCE_ARRIVED,
            time=self.env.now,
            domain_name=domain_name,
            vnf_instance=vnf_instance,
            packet=packet
        )

        with resource_vnf_instance.request() as request:
            yield request

            self.packet_log.add_event(
                event=PacketLog.PACKET_VNF_INSTANCE_ARRIVED_START_PROCESSING,
                time=self.env.now,
                domain_name=domain_name,
                vnf_instance=vnf_instance,
                packet=packet
            )

            process_delay = vnf_instance.process_delay(packet.cpu_demand)

            yield self.env.timeout(process_delay)

            self.packet_log.add_event(
                event=PacketLog.PACKET_VNF_INSTANCE_PROCESSED,
                time=self.env.now,
                domain_name=domain_name,
                vnf_instance=vnf_instance,
                packet=packet
            )

        return True

    def process_packet_over_link(self, packet: Packet, virtual_link: VirtualLink, domain: Domain):
        """
        Process the packet over the Virtual link.

        :param packet: The packet object.
        :param virtual_link: The virtual link object.
        :param domain: The domain object
        :return:
        """
        domain_name = domain.name
        resource_link = self.simpy_resource_virtual_links[virtual_link.name]

        self.packet_log.add_event(
            event=PacketLog.PACKET_VIRTUAL_LINK_ARRIVED,
            time=self.env.now,
            domain_name=domain_name,
            virtual_link=virtual_link,
            packet=packet
        )

        with resource_link.request() as request:
            yield request

            self.packet_log.add_event(
                event=PacketLog.PACKET_VIRTUAL_LINK_START_PROCESSING,
                time=self.env.now,
                domain_name=domain_name,
                virtual_link=virtual_link,
                packet=packet
            )

            transmission_delay = virtual_link.virtual_link_transmission_delay(packet)

            yield self.env.timeout(transmission_delay)

            self.packet_log.add_event(
                event=PacketLog.PACKET_VIRTUAL_LINK_PROCESSED,
                time=self.env.now,
                domain_name=domain_name,
                virtual_link=virtual_link,
                packet=packet
            )

        return True

    def inc_packet_delay(self, domain: Domain):
        """
        Increase the delay of all the packets in the simulation.
        """
        if domain.name in self.packet_in_execution:
            for packet in self.packet_in_execution[domain.name]:
                packet.increase_delay(1)
                if packet.max_delay_violated() and packet not in self.packet_delay_violated[domain.name]:
                    self.packet_log.add_event(
                        event=PacketLog.MAX_DELAY_VIOLATED,
                        time=self.env.now,
                        domain_name=domain.name,
                        packet=packet,
                    )
                    self.packet_delay_violated[domain.name].append(packet)

    def dec_sfc_instances_timeout(self, domain: Domain):
        """
        For all the active SFC Instances, decrease the timeout.

        :param domain: The domain object
        """
        sfc_instances_to_destroy = []
        for sfc_request_name, sfc_instance in domain.get_sfc_instances().items():
            if sfc_instance.get_timeout():
                timeout = sfc_instance.dec_timeout()
                if timeout == 0:
                    sfc_instances_to_destroy.append(sfc_instance)

        for sfc_instance in sfc_instances_to_destroy:
            self.del_sfc_instance(domain, sfc_instance)

    def del_sfc_instance(self, domain: Domain, sfc_instance: SFCInstance):
        """
        Destroy the SFC Instance

        :param domain:
        :param sfc_instance:
        :return:
        """
        self.sfc_instance_log.add_event(
            event=SFCInstanceLog.DESTROYED,
            time=int(self.env.now),
            domain_name=domain.name,
            sfc_instance=sfc_instance
        )
        domain.destroy_sfc_instance(sfc_instance.sfc_request.name)

        self.del_vnf_instances_not_used()

    def del_vnf_instances_not_used(self):
        """
        Remove all the VNF Instances in the environment that is not associated with any SFC Instance
        :return:
        """
        # in all the domains
        vnf_instances_in_use = dict()
        vnf_instances_associates_with_sfc_instances = dict()

        for domain_name, domain in self.domains.items():
            for node_name, node in domain.nodes.items():
                for vnf_instance_name, vnf_instance in node.vnf_instances.items():
                    vnf_instances_in_use[vnf_instance_name] = vnf_instance

            for sfc_instance_name, sfc_instance in domain.get_sfc_instances().items():
                for vnf_instance_name, vnf_instance in sfc_instance.vnf_instances.items():
                    vnf_instances_associates_with_sfc_instances[vnf_instance.name] = vnf_instance

        aux_vnf_instances_associates_with_sfc_instances = list(vnf_instances_associates_with_sfc_instances.keys())
        vnf_instances_to_destroy = np.setdiff1d(list(vnf_instances_in_use.keys()),
                                                aux_vnf_instances_associates_with_sfc_instances)

        # Remove all the VNF Instances that is not associated with a SFC Instance
        for vnf_instance_name in vnf_instances_to_destroy:
            vnf_instance = vnf_instances_in_use[vnf_instance_name]
            vnf_node: Node = self.environment['nodes'][vnf_instance.node]
            vnf_node.del_vnf_instance(vnf_instance)

            # Log the VNF Instance delete.
            self.vnf_instance_log.add_event(
                event=VNFInstanceLog.DESTROYED,
                time=self.env.now,
                domain_name=vnf_node.domain_name,
                vnf_instance=vnf_instance
            )

    def sfc_requests_vnfs_are_assigned_to_compute_zone(self):
        """
        Iterate over the SFC Requested and verify if is was placed or not.

        :return:
        """
        for sfc_request_name, zone in self.sfc_request_zone_manager.items():
            zdm = self.zdsm[zone.name]

            # if sfc_request_name not in zdm.distributed_services.keys():
            #     continue

            ds = zdm.distributed_services[sfc_request_name]
            if not ds.assigned_to_zone:
                if ds.check_vnfs_assigned_to_compute_zone():
                    # SFC Request placed
                    self.distributed_service_log.add_event(
                        event=DistributedServiceLog.VNFs_ASSIGNED_TO_COMPUTE_ZONE,
                        time=self.env.now,
                        sfc_request_name=sfc_request_name,
                        zone_manager_name=zone.name
                    )
                else:
                    if ds.dec_placement_timeout() == 0:
                        # SFC Request timeout
                        self.distributed_service_log.add_event(
                            event=DistributedServiceLog.TIMEOUT,
                            time=self.env.now,
                            sfc_request_name=sfc_request_name,
                            zone_manager_name=zone.name
                        )

    def shutdown(self):
        """
        Execute after the simulation finished.
        """

        domains = self.environment['domains']

        log: SimLog = self.environment['log']

        packet_log: PacketLog = log.get_log(SimLog.LOG_NAME_PACKET)

        for domain_name, domain in domains.items():

            for sfc_instance in list(domain.get_sfc_instances().values()):
                self.del_sfc_instance(domain, sfc_instance)

            # packet that are in execution after the simulation finished will be marked as MAX_DELAY_VIOLATED
            for packet in self.packet_in_execution[domain_name]:
                if packet not in self.packet_delay_violated[domain.name]:
                    packet_log.add_event(
                        event=PacketLog.MAX_DELAY_VIOLATED,
                        time=self.duration,
                        domain_name=domain.name,
                        packet=packet,
                    )
                    self.packet_delay_violated[domain.name].append(packet)

        log.save()

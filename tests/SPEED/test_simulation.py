import os
import unittest
import random
import networkx as nx
import simpy
import pandas as pd
import json
from SimPlacement.setup import Setup
from SimPlacement.helpers.topology_generator import TopologyGeneratorHelper
from SPEED.entities.zone import Zone
from SPEED.helpers.simulation import SimulationHelper
from SPEED.helpers.zone import ZoneHelper
from SPEED.logs.vnf_segment import VNFSegmentLog
from SPEED.simulation import SPEEDSimulation
from SimPlacement.helper import Helper

from SPEED.distributed_service_manager import DistributedServiceManager
from SPEED.logs.distributed_service import DistributedServiceLog
import networkx as nx

class SPEEDTest(unittest.TestCase):

    def test_entities_3_sfc_request_without_zone_manager(self):
        """
        Test the simulation when a service request cannot have a zone manager.
        """
        entities_file = "{}/config/entities_3_sfc_request_without_zone_manager.yml".format(os.path.dirname(os.path.abspath(__file__)))
        zone_file = "{}/config/zone_topology_4.yml".format(os.path.dirname(os.path.abspath(__file__)))
        simulation_file = "{}/config/simulation_config.yml".format(os.path.dirname(os.path.abspath(__file__)))

        environment = Setup.load_entities(
            entities_file=entities_file
        )

        environment['zones'] = ZoneHelper.load(
            data_file=zone_file,
            environment=environment
        )

        config = Helper.load_yml_file(
            data_file=simulation_file
        )

        simulation = SPEEDSimulation(
            env=simpy.Environment(),
            config=config["simulation"],
            environment=environment
        )

        # change the path where the simulation will save the logs.
        new_log_path = "{}/logs/3_sfc_request/".format(os.path.dirname(os.path.abspath(__file__)))
        simulation.log.set_log_path(new_log_path)

        simulation.run()

        log_file = "{}/{}".format(new_log_path, DistributedServiceLog.FILE_NAME)
        df = pd.read_csv(log_file, sep=";")
        self.assertEqual("Not Found", df['Zone_Manager'][0])

    def test_select_zone_manager(self):
        """
        Verify if the zone manager zone selection is working.
        """
        env = simpy.Environment()
        entities_file = "{}/config/entities_topology_build.yml".format(os.path.dirname(os.path.abspath(__file__)))
        zone_file = "{}/config/zone_topology.yml".format(os.path.dirname(os.path.abspath(__file__)))
        simulation_file = "{}/config/simulation_config.yml".format(os.path.dirname(os.path.abspath(__file__)))

        environment = Setup.load_entities(
            entities_file=entities_file
        )

        environment['zones'] = ZoneHelper.load(
            data_file=zone_file,
            environment=environment
        )

        config = Helper.load_yml_file(
            data_file=simulation_file
        )

        simulation = SPEEDSimulation(
            env=env,
            config=config["simulation"],
            environment=environment
        )

        simulation.setup()

        simulation.update_aggregated_data()

        sr_1 = environment['sfc_requests']['sr_1']
        sr_2 = environment['sfc_requests']['sr_2']
        sr_3 = environment['sfc_requests']['sr_3']

        z_sr1 = simulation.select_zone_manager(sr_1)
        z_sr2 = simulation.select_zone_manager(sr_2)
        z_sr3 = simulation.select_zone_manager(sr_3)

        self.assertEqual("z_2", z_sr1['zone_manager'].name)
        self.assertEqual("z_1", z_sr2['zone_manager'].name)
        self.assertEqual("z_2", z_sr3['zone_manager'].name)

    def test_select_zone_manager_4_level(self):
        """
        Verify if the zone manager zone selection in a 4 level zones is working.
        :return:
        """
        env = simpy.Environment()
        entities_file = "{}/config/entities_topology_build.yml".format(os.path.dirname(os.path.abspath(__file__)))
        zone_file = "{}/config/zone_topology_3.yml".format(os.path.dirname(os.path.abspath(__file__)))
        simulation_file = "{}/config/simulation_config.yml".format(os.path.dirname(os.path.abspath(__file__)))

        environment = Setup.load_entities(
            entities_file=entities_file
        )

        environment['zones'] = ZoneHelper.load(
            data_file=zone_file,
            environment=environment
        )

        config = Helper.load_yml_file(
            data_file=simulation_file
        )

        simulation = SPEEDSimulation(
            env=env,
            config=config["simulation"],
            environment=environment
        )

        simulation.setup()

        simulation.update_aggregated_data()

        sr_6 = environment['sfc_requests']['sr_6']
        z_sr6 = simulation.select_zone_manager(sr_6)
        self.assertEqual("z_0", z_sr6['zone_manager'].name)

    def test_update_aggregated_data(self):
        """
        Update all the aggregated data from all the zones.
        """
        env = simpy.Environment()
        entities_file = "{}/config/entities_topology_build.yml".format(os.path.dirname(os.path.abspath(__file__)))
        zone_file = "{}/config/zone_topology_3.yml".format(os.path.dirname(os.path.abspath(__file__)))
        simulation_file = "{}/config/simulation_config.yml".format(os.path.dirname(os.path.abspath(__file__)))

        environment = Setup.load_entities(
            entities_file=entities_file
        )

        environment['zones'] = ZoneHelper.load(
            data_file=zone_file,
            environment=environment
        )

        config = Helper.load_yml_file(
            data_file=simulation_file
        )

        simulation = SPEEDSimulation(
            env=env,
            config=config["simulation"],
            environment=environment
        )

        simulation.setup()

        simulation.update_aggregated_data()

        data = simulation.zdsm['z_0'].speed.aggregate_date()

        self.assertEqual(375.0, data['n_3_vnf_1']['cost'])

    def test_setup(self):
        """
        Test the setup simulation.
        """
        env = simpy.Environment()
        entities_file = "{}/config/entities_topology_build.yml".format(os.path.dirname(os.path.abspath(__file__)))
        zone_file = "{}/config/zone_topology.yml".format(os.path.dirname(os.path.abspath(__file__)))
        simulation_file = "{}/config/simulation_config.yml".format(os.path.dirname(os.path.abspath(__file__)))

        environment = Setup.load_entities(
            entities_file=entities_file
        )

        environment['zones'] = ZoneHelper.load(
            data_file=zone_file,
            environment=environment
        )

        config = Helper.load_yml_file(
            data_file=simulation_file
        )

        simulation = SPEEDSimulation(
            env=env,
            config=config["simulation"],
            environment=environment
        )

        simulation.setup()

        simulation.update_aggregated_data()

        self.assertEqual(5, len(simulation.domain_zone))

    def test_select_zone_manager_parent(self):
        """
        Select the zone manager until the parent zone.
        """
        env = simpy.Environment()
        entities_file = "{}/config/entities_topology_build.yml".format(os.path.dirname(os.path.abspath(__file__)))
        zone_file = "{}/config/zone_topology_3.yml".format(os.path.dirname(os.path.abspath(__file__)))
        simulation_file = "{}/config/simulation_config.yml".format(os.path.dirname(os.path.abspath(__file__)))

        environment = Setup.load_entities(
            entities_file=entities_file
        )

        environment['zones'] = ZoneHelper.load(
            data_file=zone_file,
            environment=environment
        )

        config = Helper.load_yml_file(
            data_file=simulation_file
        )

        simulation = SPEEDSimulation(
            env=env,
            config=config["simulation"],
            environment=environment
        )

        simulation.setup()

        simulation.update_aggregated_data()

        sr_1 = environment['sfc_requests']['sr_1']
        z_sr1 = simulation.select_zone_manager(sr_1)

        sr_7 = environment['sfc_requests']['sr_7']
        z_sr7 = simulation.select_zone_manager(sr_7)

        self.assertEqual("z_1", z_sr1['zone_manager'].name)
        self.assertEqual("z_0", z_sr7['zone_manager'].name)

    def test_select_segmentation_plan(self):
        """
        Select the segmentation plan based on the zone manager selected, and the valid placement plans.
        """
        entities_file = "{}/config/entities_topology_build.yml".format(os.path.dirname(os.path.abspath(__file__)))
        zone_file = "{}/config/zone_topology_3.yml".format(os.path.dirname(os.path.abspath(__file__)))
        simulation_file = "{}/config/simulation_config.yml".format(os.path.dirname(os.path.abspath(__file__)))

        environment = Setup.load_entities(
            entities_file=entities_file
        )

        environment['zones'] = ZoneHelper.load(
            data_file=zone_file,
            environment=environment
        )

        config = Helper.load_yml_file(
            data_file=simulation_file
        )

        simulation = SPEEDSimulation(
            env=simpy.Environment(),
            config=config["simulation"],
            environment=environment
        )

        simulation.setup()

        simulation.update_aggregated_data()

        sr_1 = environment['sfc_requests']['sr_1']
        z_sr1 = simulation.select_zone_manager(sr_1)
        zone_manager: Zone = z_sr1['zone_manager']
        dsm: DistributedServiceManager = simulation.zdsm[zone_manager.name]
        selected_segmentation_plan = dsm.speed.select_segmentation_plan(z_sr1['plans'])

        self.assertEqual(1, len(selected_segmentation_plan['segments']))

    def test_select_zones_for_the_segmentation_plan(self):
        """
        Select the child zones of the manager zone for each segment VNF Segment in the plan.
        """
        entities_file = "{}/config/entities_topology_build.yml".format(os.path.dirname(os.path.abspath(__file__)))
        zone_file = "{}/config/zone_topology_3.yml".format(os.path.dirname(os.path.abspath(__file__)))
        simulation_file = "{}/config/simulation_config.yml".format(os.path.dirname(os.path.abspath(__file__)))

        environment = Setup.load_entities(
            entities_file=entities_file
        )

        environment['zones'] = ZoneHelper.load(
            data_file=zone_file,
            environment=environment
        )

        config = Helper.load_yml_file(
            data_file=simulation_file
        )

        simulation = SPEEDSimulation(
            env=simpy.Environment(),
            config=config["simulation"],
            environment=environment
        )

        simulation.setup()

        simulation.update_aggregated_data()

        img_file = "{}/img/zone_topology_sim.png".format(os.path.dirname(os.path.abspath(__file__)))
        ZoneHelper.save_image(
            zones=environment['zones'],
            title="Zones Topology 4",
            file_name=img_file,
            img_width=15,
            img_height=15
        )

        sr_1 = environment['sfc_requests']['sr_1']
        z_sr1 = simulation.select_zone_manager(sr_1)
        zone_manager: Zone = z_sr1['zone_manager']

        dsm: DistributedServiceManager = simulation.zdsm[zone_manager.name]

        selected_segmentation_plan = dsm.speed.select_segmentation_plan(z_sr1['plans'])

        selected_child_zones = dsm.select_zones_to_vnf_segments(selected_segmentation_plan)

        self.assertEqual(['vnf_1', 'vnf_2'], selected_child_zones['z_2']['vnfs'])

    def test_select_zones_for_the_segmentation_plan_parallel(self):
        """
        Running the process to select the vnf segments in parallel.
        """
        entities_file = "{}/config/entities_2_sfc_request.yml".format(os.path.dirname(os.path.abspath(__file__)))
        zone_file = "{}/config/zone_topology_4.yml".format(os.path.dirname(os.path.abspath(__file__)))
        simulation_file = "{}/config/simulation_config.yml".format(os.path.dirname(os.path.abspath(__file__)))

        environment = Setup.load_entities(
            entities_file=entities_file
        )

        environment['zones'] = ZoneHelper.load(
            data_file=zone_file,
            environment=environment
        )

        config = Helper.load_yml_file(
            data_file=simulation_file
        )

        simulation = SPEEDSimulation(
            env=simpy.Environment(),
            config=config["simulation"],
            environment=environment
        )

        simulation.run()

        self.assertTrue(True)

    def test_entities_2_sfc_request_distributed(self):
        """
        Verify if the service if select multiple zones to place the vnfs
        """
        entities_file = "{}/config/entities_2_sfc_request.yml".format(os.path.dirname(os.path.abspath(__file__)))
        zone_file = "{}/config/zone_topology_4.yml".format(os.path.dirname(os.path.abspath(__file__)))
        simulation_file = "{}/config/simulation_config.yml".format(os.path.dirname(os.path.abspath(__file__)))

        environment = Setup.load_entities(
            entities_file=entities_file
        )

        environment['zones'] = ZoneHelper.load(
            data_file=zone_file,
            environment=environment
        )

        config = Helper.load_yml_file(
            data_file=simulation_file
        )

        simulation = SPEEDSimulation(
            env=simpy.Environment(),
            config=config["simulation"],
            environment=environment
        )

        # change the path where the simulation will save the logs.
        new_log_path = "{}/logs/2_sfc_request/".format(os.path.dirname(os.path.abspath(__file__)))
        simulation.log.set_log_path(new_log_path)

        simulation.run()

        log_file = "{}/{}".format(new_log_path, DistributedServiceLog.FILE_NAME)
        df = pd.read_csv(log_file, sep=";")

        # Print logs test (don't remove)
        # print(df)

        img_file = "{}/img/zone_topology_4.png".format(os.path.dirname(os.path.abspath(__file__)))
        ZoneHelper.save_image(
            zones=environment['zones'],
            title="Zones Topology Example",
            file_name=img_file,
            img_width=10,
            img_height=10
        )

        SimulationHelper.print_environment_topology(
            environment=environment
        )

        # self.assertEqual("z_0", df['Zone_Manager'][0])
        # self.assertEqual("z_1", df['Zone_Manager'][1])

    def test_entities_1_sfc_request_placement_timeout(self):
        """
        Verify if the service if select multiple zones to place the vnfs
        """
        entities_file = "{}/config/entities_1_sfc_request_timeout.yml".format(os.path.dirname(os.path.abspath(__file__)))
        zone_file = "{}/config/zone_topology_4.yml".format(os.path.dirname(os.path.abspath(__file__)))
        simulation_file = "{}/config/simulation_config.yml".format(os.path.dirname(os.path.abspath(__file__)))

        environment = Setup.load_entities(
            entities_file=entities_file
        )

        environment['zones'] = ZoneHelper.load(
            data_file=zone_file,
            environment=environment
        )

        config = Helper.load_yml_file(
            data_file=simulation_file
        )

        simulation = SPEEDSimulation(
            env=simpy.Environment(),
            config=config["simulation"],
            environment=environment
        )

        # change the path where the simulation will save the logs.
        new_log_path = "{}/logs/1_sfc_request_timeout/".format(os.path.dirname(os.path.abspath(__file__)))
        simulation.log.set_log_path(new_log_path)

        simulation.run()

        log_file = "{}/{}".format(new_log_path, VNFSegmentLog.FILE_NAME)
        df = pd.read_csv(log_file, sep=";")

        self.assertEqual("TIMEOUT", df['Event'][0])

    def test_entities_1_sfc_request_placement(self):
        """
        Verify if the service if select multiple zones to place the vnfs
        """
        entities_file = "{}/config/entities_1_sfc_request_placement.yml".format(os.path.dirname(os.path.abspath(__file__)))
        zone_file = "{}/config/zone_topology_4.yml".format(os.path.dirname(os.path.abspath(__file__)))
        simulation_file = "{}/config/simulation_config.yml".format(os.path.dirname(os.path.abspath(__file__)))

        environment = Setup.load_entities(
            entities_file=entities_file
        )

        environment['zones'] = ZoneHelper.load(
            data_file=zone_file,
            environment=environment
        )

        config = Helper.load_yml_file(
            data_file=simulation_file
        )

        simulation = SPEEDSimulation(
            env=simpy.Environment(),
            config=config["simulation"],
            environment=environment
        )

        # change the path where the simulation will save the logs.
        new_log_path = "{}/logs/entities_1_sfc_request_placement/".format(os.path.dirname(os.path.abspath(__file__)))
        simulation.log.set_log_path(new_log_path)

        simulation.run()

        SimulationHelper.print_environment_topology(
            environment=environment
        )

        log_file = "{}/{}".format(new_log_path, VNFSegmentLog.FILE_NAME)
        df = pd.read_csv(log_file, sep=";")

    def test_entities_2_sfc_request_placement_only_one(self):
        """
        Allocate the resource in the compute zone after the zone selection to execute the VNFs.

        The second SFC Request will fail due to lack of resources.
        """
        entities_file = "{}/config/entities_2_sfc_request_placement.yml".format(os.path.dirname(os.path.abspath(__file__)))
        zone_file = "{}/config/zone_topology_4.yml".format(os.path.dirname(os.path.abspath(__file__)))
        simulation_file = "{}/config/simulation_config_2.yml".format(os.path.dirname(os.path.abspath(__file__)))

        environment = Setup.load_entities(
            entities_file=entities_file
        )

        environment['zones'] = ZoneHelper.load(
            data_file=zone_file,
            environment=environment
        )

        config = Helper.load_yml_file(
            data_file=simulation_file
        )

        simulation = SPEEDSimulation(
            env=simpy.Environment(),
            config=config["simulation"],
            environment=environment
        )

        # change the path where the simulation will save the logs.
        new_log_path = "{}/logs/entities_2_sfc_request_placement_only_one/".format(os.path.dirname(os.path.abspath(__file__)))
        simulation.log.set_log_path(new_log_path)

        simulation.run()

        SimulationHelper.print_environment_topology(
            environment=environment
        )

        log_file = "{}/{}".format(new_log_path, DistributedServiceLog.FILE_NAME)
        df = pd.read_csv(log_file, sep=";")

        self.assertEqual("COMPUTE_ZONE_NO_RESOURCE", df['Event'][0])

    def test_random(self):
        """
        Test the random zone selection.
        """
        random.seed(1)

        entities_file = "{}/config/entities_2_sfc_request_placement.yml".format(os.path.dirname(os.path.abspath(__file__)))
        zone_file = "{}/config/zone_topology_4.yml".format(os.path.dirname(os.path.abspath(__file__)))
        simulation_file = "{}/config/simulation_config_2.yml".format(os.path.dirname(os.path.abspath(__file__)))

        environment = Setup.load_entities(
            entities_file=entities_file
        )

        environment['zones'] = ZoneHelper.load(
            data_file=zone_file,
            environment=environment
        )

        config = Helper.load_yml_file(
            data_file=simulation_file
        )

        simulation = SPEEDSimulation(
            env=simpy.Environment(),
            config=config["simulation"],
            environment=environment
        )

        # change the path where the simulation will save the logs.
        new_log_path = "{}/logs/entities_2_sfc_request_placement_only_one/".format(os.path.dirname(os.path.abspath(__file__)))
        simulation.log.set_log_path(new_log_path)

        os.environ["ALGORITHM"] = "random"

        simulation.run()

        # SimulationHelper.print_environment_topology(
        #     environment=environment
        # )

        log_file = "{}/{}".format(new_log_path, DistributedServiceLog.FILE_NAME)
        df = pd.read_csv(log_file, sep=";")

        self.assertEqual("COMPUTE_ZONE_NO_RESOURCE", df['Event'][0])

        # dot_str = ZoneHelper.build_dot_from_zone_file(
        #     file=zone_file
        # )
        #
        # print(dot_str)

    def test_greedy(self):
        """
        Test the random zone selection.
        """
        entities_file = "{}/config/greedy/files/10_0.yml".format(os.path.dirname(os.path.abspath(__file__)))
        zone_file = "{}/config/greedy/config/zone_topology.yml".format(os.path.dirname(os.path.abspath(__file__)))
        simulation_file = "{}/config/greedy/config/config_simulation.yml".format(os.path.dirname(os.path.abspath(__file__)))

        environment = Setup.load_entities(
            entities_file=entities_file
        )

        environment['zones'] = ZoneHelper.load(
            data_file=zone_file,
            environment=environment
        )

        config = Helper.load_yml_file(
            data_file=simulation_file
        )

        simulation = SPEEDSimulation(
            env=simpy.Environment(),
            config=config["simulation"],
            environment=environment
        )

        # change the path where the simulation will save the logs.
        new_log_path = "{}/config/greedy/logs/".format(os.path.dirname(os.path.abspath(__file__)))
        simulation.log.set_log_path(new_log_path)

        os.environ["ALGORITHM"] = "greedy"

        simulation.run()

        SimulationHelper.print_environment_topology(
            environment=environment
        )

        log_file = "{}/{}".format(new_log_path, DistributedServiceLog.FILE_NAME)
        df = pd.read_csv(log_file, sep=";")

        self.assertEqual("PLACED", df['Event'][0])

        img_file = "{}/config/greedy/zone_topology.png".format(os.path.dirname(os.path.abspath(__file__)))
        ZoneHelper.save_image(
            zones=environment['zones'],
            title="",
            file_name=img_file,
            img_width=10,
            img_height=10
        )

    def test_run_experiment_A1(self):
        """
        Run the experiment A1
        """
        zone_file = "{}/../../experiments/A1/config/zone_topology.yml".format(os.path.dirname(os.path.abspath(__file__)))
        simulation_file = "{}/../../experiments/A1/config/config_simulation.yml".format(os.path.dirname(os.path.abspath(__file__)))

        requests = [10]
        rounds = 1

        for i in range(0, len(requests)):
            for j in range(0, rounds):
                entities_file = "{}/../../experiments/A1/files/{}_{}.yml".format(os.path.dirname(os.path.abspath(__file__))
                                                                            , requests[i], j)

                environment = Setup.load_entities(
                    entities_file=entities_file
                )

                environment['zones'] = ZoneHelper.load(
                    data_file=zone_file,
                    environment=environment
                )

                config = Helper.load_yml_file(
                    data_file=simulation_file
                )

                simulation = SPEEDSimulation(
                    env=simpy.Environment(),
                    config=config["simulation"],
                    environment=environment
                )

                # change the path where the simulation will save the logs.

                new_log_path = "{}/../../experiments/A1/logs/{}_{}".format(os.path.dirname(os.path.abspath(__file__))
                                                                            ,requests[i], j)
                simulation.log.set_log_path(new_log_path)

                simulation.run()

                img_file = "{}/../../experiments/A1/imgs/{}_{}_zone.png".format(os.path.dirname(os.path.abspath(__file__)),
                                                                           requests[i], j)
                ZoneHelper.save_image(
                    zones=environment['zones'],
                    title="Exp 1 - {}_{}".format(i, j),
                    file_name=img_file,
                    img_width=15,
                    img_height=15
                )

                img_topology = "{}/../../experiments/A1/imgs/{}_{}_topology.png".format(os.path.dirname(os.path.abspath(__file__)),
                                                                           requests[i], j)
                environment['topology'].save_image(
                    environment['topology'].get_graph(),
                    "Full Topology {}_{}".format(i, j),
                    img_topology
                )

                # SimulationHelper.print_environment_topology(
                #     environment=environment
                # )
                #
                # log_file = "{}/{}".format(new_log_path, DistributedServiceLog.FILE_NAME)
                # df = pd.read_csv(log_file, sep=";")

    def test_generate_random_tree_with_max_height(self):
        """
        Generate the random tree with a max_height
        :return:
        """
        random.seed(98)
        G = ZoneHelper.generate_random_tree_with_max_height(
            max_height=4,
            num_aggregation_zones=10
        )

        # check if the amount of nodes was generated correctly
        self.assertEqual(10, len(G))

        # check if the max depth was generated correctly
        self.assertEqual(4, nx.dag_longest_path_length(G))

        # print("\n")
        # print(nx.write_network_text(G))


    def test_simulation_helper_zone_topology_generation(self):

        random.seed(1)
        zone_topology, G, leafs = SimulationHelper.zone_topology_generation(3)

        self.assertEqual(12, zone_topology['zones'].__len__())
        self.assertEqual("compute", zone_topology['zones']['C_3']['zone_type'])

        # Print the zone topology
        # print(json.dumps(zone_topology, indent=1))
        # nx.write_network_text(G)

    def test_generate_zone_topology(self):
        """
        Test the generation of the zone topology
        :return:
        """
        entities_file = "{}/logs/generate_zone_topology/10_0.yml".format(os.path.dirname(os.path.abspath(__file__)))
        # entities_file = "{}/logs/generate_zone_topology/environment.yml".format(os.path.dirname(os.path.abspath(__file__)))
        oft = "{}/logs/generate_zone_topology/topo.yml".format(os.path.dirname(os.path.abspath(__file__)))
        oft_dot = "{}/logs/generate_zone_topology/topo.dot".format(os.path.dirname(os.path.abspath(__file__)))

        environment = Setup.load_entities(
            entities_file=entities_file
        )

        zone_topology = SimulationHelper.generate_zone_topology(
            num_aggregation_zones=10,
            max_height=4,
            domains=environment['domains']
        )

        TopologyGeneratorHelper.save_file(
            output_file=oft,
            data=zone_topology
        )

        dot_str = ZoneHelper.build_dot_from_zone_file(
            file=oft
        )

        with open(oft_dot, 'w') as file:
            file.write(dot_str)

        self.assertEqual(True, False)

    def test_random_10(self):
        """
        Test the random with the 10 topology
        """
        random.seed(1)
        entities_file = "{}/logs/random/10_0.yml".format(os.path.dirname(os.path.abspath(__file__)))
        zone_file = "{}/logs/random/10_0_topo.yml".format(os.path.dirname(os.path.abspath(__file__)))
        simulation_file = "{}/config/simulation_config_2.yml".format(os.path.dirname(os.path.abspath(__file__)))

        environment = Setup.load_entities(
            entities_file=entities_file
        )

        environment['zones'] = ZoneHelper.load(
            data_file=zone_file,
            environment=environment
        )

        config = Helper.load_yml_file(
            data_file=simulation_file
        )

        simulation = SPEEDSimulation(
            env=simpy.Environment(),
            config=config["simulation"],
            environment=environment
        )

        # # change the path where the simulation will save the logs.
        # new_log_path = "{}/logs/entities_2_sfc_request_placement_only_one/".format(os.path.dirname(os.path.abspath(__file__)))
        # simulation.log.set_log_path(new_log_path)

        os.environ["ALGORITHM"] = "random"

        simulation.run()

        # SimulationHelper.print_environment_topology(
        #     environment=environment
        # )

        log_file = "{}/{}".format(new_log_path, DistributedServiceLog.FILE_NAME)
        df = pd.read_csv(log_file, sep=";")

        self.assertEqual("COMPUTE_ZONE_NO_RESOURCE", df['Event'][0])

        # dot_str = ZoneHelper.build_dot_from_zone_file(
        #     file=zone_file
        # )
        #
        # print(dot_str)

    def test_error_5(self):
        """
        Verify why the placement plan for the request 4 is not being finded.
        """
        random.seed(1)
        entities_file = "{}/config/error_5/5_4.yml".format(os.path.dirname(os.path.abspath(__file__)))
        zone_file = "{}/config/error_5/5_4_topo.yml".format(os.path.dirname(os.path.abspath(__file__)))
        simulation_file = "{}/config/error_5/config_simulation.yml".format(os.path.dirname(os.path.abspath(__file__)))

        environment = Setup.load_entities(
            entities_file=entities_file
        )

        environment['zones'] = ZoneHelper.load(
            data_file=zone_file,
            environment=environment
        )

        config = Helper.load_yml_file(
            data_file=simulation_file
        )

        simulation = SPEEDSimulation(
            env=simpy.Environment(),
            config=config["simulation"],
            environment=environment
        )

        # change the path where the simulation will save the logs.
        new_log_path = "{}/config/error_5/logs".format(os.path.dirname(os.path.abspath(__file__)))
        simulation.log.set_log_path(new_log_path)

        simulation.run()

    def test_print_generated_image_A3(self):
        """
        Generate the image from exp3
        """
        entities_file = "{}/config/A3/5_0.yml".format(os.path.dirname(os.path.abspath(__file__)))
        zone_file = "{}/config/A3/5_0_topo.yml".format(os.path.dirname(os.path.abspath(__file__)))
        simulation_file = "{}/config/A3/config_simulation.yml".format(

        os.path.dirname(os.path.abspath(__file__)))

        environment = Setup.load_entities(
            entities_file=entities_file
        )

        environment['zones'] = ZoneHelper.load(
            data_file=zone_file,
            environment=environment
        )

        config = Helper.load_yml_file(
            data_file=simulation_file
        )

        simulation = SPEEDSimulation(
            env=simpy.Environment(),
            config=config["simulation"],
            environment=environment
        )

        simulation.setup()

        simulation.update_aggregated_data()

        sr_1 = environment['sfc_requests']['sr_1']

        z_sr1 = simulation.select_zone_manager(sr_1)

        self.assertEqual("z_2", z_sr1['zone_manager'].name)

        # img_file = "{}/config/A3/zone_topology.png".format(os.path.dirname(os.path.abspath(__file__)))
        # ZoneHelper.save_image(
        #     zones=environment['zones'],
        #     title="",
        #     file_name=img_file,
        #     img_width=50,
        #     img_height=50
        # )
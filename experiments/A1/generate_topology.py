import os
import random
import networkx as nx
import glob

from SimPlacement.helpers.topology_generator import TopologyGeneratorHelper
from SPEED.helpers.simulation import SimulationHelper

# Amount of SFC Requests
num_sfc_requests = [5, 20, 50, 80, 100]

# Amount of domains in each iteration
# num_domains = [5, 10, 20, 30, 40, 50]
# num_domains = [66]

# Amount of rounds (for each round a set of files will be created)
num_rounds = 10

path = os.path.dirname(os.path.abspath(__file__))
files_path = "{}/files/*".format(path)
files = glob.glob(files_path)
for f in files:
    os.remove(f)

for i in range(0, num_rounds):

    # The seed of the topology generation
    random.seed(i)

    j = -1
    for num_sfc_request in num_sfc_requests:
        j += 1
        fe = "{}/config/config_entities.yml".format(path)
        ofe = "{}/files/{}_{}.yml".format(path, num_sfc_request, i)
        oft = "{}/files/{}_{}_topo.yml".format(path, num_sfc_request, i)

        config_topology = dict()
        config_topology['num_vnfs'] = 10
        config_topology['num_sfcs'] = 3
        config_topology['num_nodes'] = 200
        config_topology['num_ues'] = 5
        config_topology['num_sfc_requests'] = num_sfc_request
        config_topology['num_domains'] = 66

        aux = dict()
        aux['inter_domain'] = 0.02
        aux['intra_domain'] = 0.30
        config_topology['link_probability'] = aux

        TopologyGeneratorHelper.generate(
            config_file=fe,
            output_file=ofe,
            config_topology=config_topology
        )

        zoo_topology_file = "{}/zoo_topology/topology-zoo.org_files_Internode.gml".format(path)

        # Load the GML file
        G = nx.read_gml(
            path=zoo_topology_file,
            label="id"
        )

        # Compute the centrality of all the nodes in the topology
        centrality = nx.degree_centrality(G)

        # Sort the nodes by the centrality, the first nodes has higher centrality
        s = sorted(centrality.items(), key=lambda x: x[1], reverse=True)

        SimulationHelper.convert_environment_using_topology_zoo(
            zoo_topology=zoo_topology_file,
            zone_root=s[i][0],
            environment_file=ofe,
            topo_file = oft
        )

        # # load the generated environment
        # topology = TopologyGeneratorHelper.load_yml_file(
        #     data_file=ofe
        # )



        # zone_topology = SimulationHelper.generate_zone_topology(
        #     num_aggregation_zones=num_aggregation_zones[j],
        #     max_height=max_height[j],
        #     domains=topology['domains']
        # )
        #
        # TopologyGeneratorHelper.save_file(
        #     output_file=oft,
        #     data=zone_topology
        # )

        # C_1:
        #     zone_type: "compute"
        #     parent_zone: "A_1"
        #     domain: "dom_0"

        # # Print the zone topology
        # print(json.dumps(zone_topology, indent=1))
        # nx.write_network_text(G)


        # Generate topology image
        # img_file = "{}/imgs/topology_{}_{}.png".format(os.path.dirname(os.path.abspath(__file__)), num_domain, i)
        # environment = Setup.load_entities(ofe)
        # topology: Topology = environment['topology']
        #
        # topology.save_image(
        #     topology.get_graph(),
        #     title="",
        #     file_name=img_file,
        #     img_width=20,
        #     img_height=20
        # )
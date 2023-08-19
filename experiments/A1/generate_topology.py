import os
import random

from SimPlacement.helpers.topology_generator import TopologyGeneratorHelper
from SPEED.helpers.simulation import SimulationHelper

# Amount of SFC Requests
num_sfc_requests = 50

# Amount of domains in each iteration
num_domains = [5, 10, 20, 30, 40, 50]

# Amount of rounds (for each round a set of files will be created)
num_rounds = 2

# Amount of aggregation zones
num_aggregation_zones = [20, 20, 20, 20, 20, 20]

# The max height of the topology (create a topology were the compute zone of low level have less nodes)
# 1 - Global Cloud Provider
# 2 - National Cloud Provider
# 3 - Regional Cloud Provider
# 4 - Local Edge Provider
max_height = [4, 4, 4, 4, 4, 4]

path = os.path.dirname(os.path.abspath(__file__))

for i in range(0, num_rounds):

    # The seed of the topology generation
    random.seed(i)

    for num_domain in num_domains:

        fe = "{}/config/config_entities.yml".format(path)
        ofe = "{}/files/{}_{}.yml".format(path, num_domain, i)
        oft = "{}/files/{}_{}_topo.yml".format(path, num_domain, i)

        config_topology = dict()
        config_topology['num_vnfs'] = 10
        config_topology['num_sfcs'] = 3
        config_topology['num_nodes'] = 1000
        config_topology['num_ues'] = 5
        config_topology['num_sfc_requests'] = num_sfc_requests
        config_topology['num_domains'] = num_domain

        aux = dict()
        aux['inter_domain'] = 0.02
        aux['intra_domain'] = 0.30
        config_topology['link_probability'] = aux

        topology = TopologyGeneratorHelper.generate(
            config_file=fe,
            output_file=ofe,
            config_topology=config_topology
        )

        zone_topology = SimulationHelper.generate_zone_topology(
            num_aggregation_zones=num_aggregation_zones[i],
            max_height=max_height[i],
            domains=topology['domains']
        )

        TopologyGeneratorHelper.save_file(
            output_file=oft,
            data=zone_topology
        )

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
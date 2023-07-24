import os
import random

import networkx as nx
from SimPlacement.helpers.topology_generator import TopologyGeneratorHelper
from SimPlacement.setup import Setup
from SimPlacement.topology import Topology

num_sfc_requests = 50
num_domains = [5, 10, 25, 50]
num_rounds = 10

path = os.path.dirname(os.path.abspath(__file__))

for i in range(0, num_rounds):
    random.seed(i)

    for num_domain in num_domains:

        G = nx.random_tree(n=num_domain, seed=i)

        leafs [x for x in G.nodes_() if G.out_degree(x) == 0 and G.in_degree(x) == 1]
        nx.write_network_text(tree, sources=[0])
        print(leafs)
        exit()
        continue
        fe = "{}/config/config_entities.yml".format(path)
        ofe = "{}/files/{}_{}.yml".format(path, num_domain, i)

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

        TopologyGeneratorHelper.generate(
            config_file=fe,
            output_file=ofe,
            config_topology=config_topology
        )

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

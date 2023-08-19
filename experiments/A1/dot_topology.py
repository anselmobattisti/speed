from SimPlacement.helpers.topology_generator import TopologyGeneratorHelper
from SPEED.helpers.zone import ZoneHelper

#
# # Set the maximum height for the tree
# max_height = 5
#
# G = ZoneHelper.generate_random_tree_with_max_height(max_height)
from SPEED.helpers.simulation import SimulationHelper

# # Generate the random tree
# internet_network = generate_random_tree_with_max_height(max_height)
#
# # Plot the tree
# pos = nx.spring_layout(internet_network)
# nx.draw(internet_network, pos, with_labels=True, node_size=500, font_size=10, font_weight='bold')
# plt.title(f"Random Internet Network (Max Height: {max_height})")
# plt.show()

# import networkx as nx

# # Create a sample graph (you can replace this with your actual graph)
# G = nx.Graph()
# G.add_edges_from([(1, 2), (2, 3), (3, 4), (4, 5), (5, 6), (4, 7)])
#
# # Find leaf nodes (nodes with degree 1)
# leaf_nodes = [node for node, degree in G.degree() if degree == 1]
#
# print("Leaf nodes:", leaf_nodes)
#
# import random
#
# def fibonacci(n):
#     fib_sequence = [1, 1]
#     while len(fib_sequence) < n:
#         next_fib = fib_sequence[-1] + fib_sequence[-2]
#         fib_sequence.append(next_fib)
#     return fib_sequence
#
# def generate_random_number():
#     n = 5  # Generate the first 5 Fibonacci numbers (adjust this as needed)
#     fib_sequence = fibonacci(n)
#     numbers = list(range(1, n+1))
#     weights = fib_sequence[::-1]  # Reverse the Fibonacci sequence for higher weights on smaller numbers
#
#     random_number = random.choices(numbers, weights=weights)[0]
#     return random_number
#
# # Generate and print 10 random numbers
# for _ in range(10):
#     print(generate_random_number())

# zone_topology, G, leafs = SimulationHelper.zone_topology_generation(3)
#
# import networkx as nx
#
# max_height = 5
# num_domains = 20
# height = -1
#
# while height != max_height:
#
#     tree: nx.DiGraph =  nx.random_tree(n=num_domains, create_using=nx.DiGraph)
#
#     # Get the longest path length in the DiGraph
#     height = nx.dag_longest_path_length(tree)
#
#     print(tree.nodes)
#
# nx.write_network_text(tree)
#

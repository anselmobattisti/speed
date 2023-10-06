import matplotlib.pyplot as plt
import networkx as nx

J = nx.read_gml("./zoo_topology/topology-zoo.org_files_Internode.gml")

print(len(J.nodes))

nx.draw(J)
plt.show()
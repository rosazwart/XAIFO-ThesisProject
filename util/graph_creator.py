import networkx as nx

def create_graph(nodes, edges):
    G = nx.from_pandas_edgelist(edges, source='subject_id', target='object_id')
    
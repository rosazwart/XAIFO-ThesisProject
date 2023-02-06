import networkx as nx
import matplotlib.pyplot as plt

def create_graph(edges, source_colname, target_colname, file_name):
    G = nx.from_pandas_edgelist(edges, source=source_colname, target=target_colname)
    
    nx.draw(G, with_labels=True, node_size=800, font_size=6)
    
    plt.savefig(f'output/{file_name}')
    
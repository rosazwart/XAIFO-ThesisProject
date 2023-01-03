import os
import pandas as pd

data_folder = 'data'

def load_edges_from_csv():
    data_path = os.path.join(data_folder, 'graph_edges_v2022-01-11.csv')
    edges_data = pd.read_csv(data_path)
    
    print('Loaded edges with attributes:', edges_data.columns.values)
    
    return edges_data

def load_nodes_from_csv():
    data_path = os.path.join(data_folder, 'graph_nodes_v2022-01-11.csv')
    nodes_data = pd.read_csv(data_path)
    
    print('Loaded nodes with attributes:', nodes_data.columns.values)
    
    return nodes_data
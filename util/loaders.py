from util.common_util import register_info

import os
import pandas as pd

INPUT_FOLDER = 'data'
OUTPUT_FOLDER = 'output'

def load_monarch_nodes_from_csv():
    """
        Load all nodes representing the acquired data from the Monarch Initiative.
    """
    data_path = os.path.join(OUTPUT_FOLDER, 'monarch_nodes.csv')
    nodes_data = pd.read_csv(data_path)
    
    register_info(f'Loaded nodes with attributes: {nodes_data.columns.values}')
    
    return nodes_data

def load_edges_from_csv():
    data_path = os.path.join(INPUT_FOLDER, 'graph_edges_v2022-01-11.csv')
    edges_data = pd.read_csv(data_path)
    
    print('Loaded edges with attributes:', edges_data.columns.values)
    
    return edges_data

def load_nodes_from_csv():
    data_path = os.path.join(INPUT_FOLDER, 'graph_nodes_v2022-01-11.csv')
    nodes_data = pd.read_csv(data_path)
    
    print('Loaded nodes with attributes:', nodes_data.columns.values, '\n')
    
    return nodes_data

def load_entity_sample(all_nodes, semantic_group):
    return all_nodes.loc[all_nodes['semantic_groups'] == semantic_group].sample(n=5)
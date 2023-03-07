from util.common import register_info

import os
import pandas as pd

INPUT_FOLDER = 'data'
OUTPUT_FOLDER = 'output'

def get_input_data_path(file_name):
    return os.path.join(INPUT_FOLDER, file_name)

def load_monarch_nodes_from_csv():
    """
        Load all nodes representing the acquired data from the Monarch Initiative.
    """
    data_path = os.path.join(OUTPUT_FOLDER, 'monarch_nodes.csv')
    nodes_data = pd.read_csv(data_path)
    
    register_info(f'Loaded {nodes_data.shape[0]} nodes with attributes: {nodes_data.columns.values}')
    
    return nodes_data
import pandas as pd

import analyzer.graphstructure as graphstructure

from util.loaders import get_input_data_path

def analyzePrevData():
    data_path = get_input_data_path('graph_nodes_v2022-01-11.csv')
    nodes = pd.read_csv(data_path)
    print('Loaded nodes with attributes:', nodes.columns.values)
    
    data_path = get_input_data_path('graph_edges_v2022-01-11.csv')
    edges = pd.read_csv(data_path)
    print('Loaded edges with attributes:', edges.columns.values)
    
    edge_colmapping = {
        'relations': 'property_label',
        'subject': 'subject_id',
        'object': 'object_id'
    }
    
    node_colmapping = {
        'node_id': 'id',
        'semantics': 'semantic_groups'
    }
    
    graphstructure.getConcepts(nodes, node_colmapping)
    graphstructure.getRelations(edges, edge_colmapping)
    graphstructure.getConnectionSummary(edges, nodes, 
                                        edge_colmapping, node_colmapping,
                                        'prev_concepts.png', 'prev_triplets.csv')

if __name__ == "__main__":
    analyzePrevData()
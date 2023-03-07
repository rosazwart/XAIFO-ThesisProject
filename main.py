import pandas as pd

import analyzer.graphstructure as graphstructure

import monarch.fetcher as monarch_fetcher

from util.loaders import get_input_data_path, OUTPUT_FOLDER
from util.common import register_info, tuplelist2dataframe

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
    
def getMonarchAssociations():
    nodes_list = [
        'MONDO:0010679',
        'HGNC:2928'
    ]
    
    seed_neighbours_id_list = monarch_fetcher.get_seed_neighbour_node_ids(seed_id_list=nodes_list, rows=2000)
    orthopheno_id_list = monarch_fetcher.get_orthopheno_node_ids(first_seed_id_list=nodes_list, depth=2, rows=2000)
    
    register_info(f'A total of {len(seed_neighbours_id_list)} first order neighbours of given seeds have been found')
    register_info(f'A total of {len(orthopheno_id_list)} orthologs/phenotypes have been found.')
    
    all_nodes_id_list = seed_neighbours_id_list.union(orthopheno_id_list)
    all_nodes_id_list.update(nodes_list)
    register_info(f'A total of {len(all_nodes_id_list)} nodes have been found for which from and to associations will be retrieved.')
        
    all_associations = monarch_fetcher.get_seed_first_order_associations(seed_id_list=all_nodes_id_list, rows=1000, exclude_new_ids=True)
    tuplelist2dataframe(all_associations).to_csv(f'{OUTPUT_FOLDER}/monarch_associations.csv', index=False)
    register_info('All MONARCH associations are saved into monarch_associations.csv')
    
    return all_associations

if __name__ == "__main__":
    getMonarchAssociations()
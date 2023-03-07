# TODO: split this file into correct modules

from util.common import register_info, draw_graph_from_edges

import util.loaders as loaders
import monarch.fetcher as monarch_fetcher
import util.graph_builder as graph_builder
import util.mapper as mapper
import util.cypher_query_builder as cypher_query_builder
    
def analyze_bioknowledgereviewer_results():
    # Load the edges and nodes of the graph generated from Monarch
    all_edges = loaders.load_edges_from_csv()
    all_nodes = loaders.load_nodes_from_csv()
    
    edge_colmap = {
        'relations': 'property_label',
        'subject': 'subject_id',
        'object': 'object_id'
    }
    
    node_colmap = {
        'node_id': 'id',
        'semantics': 'semantic_groups'
    }
    
    analyzeData(all_edges, all_nodes, edge_colmap, node_colmap, 'bioknowledgereviewer_concepts.png', 'bioknowledgereviewer_triplets.csv')
    
def fetch_data():
    nodes_list = [
        'MONDO:0010679',
        'HGNC:2928'
    ]
    
    seed_neighbours_id_list = monarch_fetcher.get_seed_neighbour_node_ids(seed_id_list=nodes_list, rows=2000)
    orthopheno_id_list = monarch_fetcher.get_orthopheno_node_ids(first_seed_id_list=nodes_list, depth=2, rows=2000)
    
    register_info(f'A total of {len(seed_neighbours_id_list)} first order neighbours have been found')
    register_info(f'A total of {len(orthopheno_id_list)} orthologs/phenotypes have been found.')
    
    all_nodes_id_list = seed_neighbours_id_list.union(orthopheno_id_list)
    all_nodes_id_list.update(nodes_list)
    register_info(f'A total of {len(all_nodes_id_list)} nodes have been found for which from and to associations will be retrieved.')
    
    all_associations = monarch_fetcher.get_seed_first_order_associations(seed_id_list=all_nodes_id_list, rows=1000, exclude_new_ids=True)
    
    knowledge_graph = graph_builder.KnowledgeGraph(all_associations)
    all_edges, all_nodes = knowledge_graph.generate_dataframes()
    
    mapped_nodes_edges = mapper.Mapper(all_edges=all_edges, all_nodes=all_nodes)
    mapped_nodes_edges.all_edges_with_nodes.to_csv('output/associations_notmapped.csv', index=False)
    mapped_nodes_edges.include_genotype_gene_relations()
    
    # Save into csv files
    mapped_nodes_edges.all_edges.to_csv('output/monarch_edges.csv', index=False)
    mapped_nodes_edges.all_nodes.to_csv('output/monarch_nodes.csv', index=False)
    
    cypher_query_builder.build_queries(mapped_nodes_edges.all_nodes, mapped_nodes_edges.all_edges)
    
    edge_colmap = {
        'relations': 'relation_label',
        'subject': 'subject',
        'object': 'object'
    }
    
    node_colmap = {
        'node_id': 'id',
        'semantics': 'semantic'
    }
    
    analyzeData(all_edges, all_nodes, edge_colmap, node_colmap, 'monarch_concepts.png', 'monarch_triplets.csv')

if __name__ == "__main__":
    #analyze_bioknowledgereviewer_results()
    fetch_data()
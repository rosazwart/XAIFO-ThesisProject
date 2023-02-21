from util.common_util import register_info, draw_graph_from_edges

import util.loaders as loaders
import util.monarch_fetcher.monarch_fetcher as monarch_fetcher
import util.graph_builder as graph_builder
import util.mapper as mapper
import util.cypher_query_builder as cypher_query_builder

def analyzeData(all_edges, all_nodes, edge_colmap: dict, node_colmap: dict, graph_image_file_name, triplets_file_name):
    """
        Analyze given data by getting all unique properties and semantic groups, unique triplets etc.
        :param all_edges: dataframe of edges in the format resulting from BioKnowledgeReviewer Monarch Module
        :param all_nodes: dataframe of nodes in the format resulting from BioKnowledgeReviewer Monarch module
    """
    # Get all unique properties and semantic groups
    property_grouped = all_edges[edge_colmap['relations']].unique()
    register_info(f'There are {len(property_grouped)} properties: {property_grouped}')
    
    semantic_grouped = all_nodes[node_colmap['semantics']].unique()
    register_info(f'There are {len(semantic_grouped)} semantic groups: {semantic_grouped}')
    
    # Retrieve relations and their subjects/objects
    edge_entries = all_edges[[edge_colmap['subject'], edge_colmap['relations'], edge_colmap['object']]]
    
    joined_subjects = edge_entries.merge(all_nodes, left_on=edge_colmap['subject'], right_on=node_colmap['node_id'])[[node_colmap['semantics'], edge_colmap['relations'], edge_colmap['object']]]
    joined_subjects.rename(columns={node_colmap['semantics']: 'semantic_groups_subject'}, inplace=True)
    
    joined_objects = joined_subjects.merge(all_nodes, left_on=edge_colmap['object'], right_on=node_colmap['node_id'])[['semantic_groups_subject', edge_colmap['relations'], node_colmap['semantics']]]
    joined_objects.rename(columns={node_colmap['semantics']: 'semantic_groups_object'}, inplace=True)
    
    # Look at unique subject/object pairs and relation pairs
    subject_object_pairs = joined_objects[['semantic_groups_subject', 'semantic_groups_object']].drop_duplicates().reset_index(drop=True)
    
    graph_builder.draw_graph_from_edges(subject_object_pairs, source_colname='semantic_groups_subject', target_colname='semantic_groups_object', file_name=graph_image_file_name)
    
    subject_property_object_triplets = joined_objects.drop_duplicates().reset_index(drop=True)
    subject_property_object_triplets = subject_property_object_triplets.sort_values(by=edge_colmap['relations']).reset_index(drop=True)
    
    subject_property_object_triplets.rename(columns={'semantic_groups_subject': 'subject', edge_colmap['relations']: 'relation', 'semantic_groups_object': 'object'}, inplace=True)
    all_col_names = list(subject_property_object_triplets.columns.values)
    for col_name in all_col_names:
        subject_property_object_triplets[col_name] = subject_property_object_triplets[col_name].str.replace('_',' ')
        subject_property_object_triplets[col_name] = subject_property_object_triplets[col_name].fillna('undefined')
        
    subject_property_object_triplets.to_csv(f'output/{triplets_file_name}', index=False)
    
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
    
    seed_neighbours_id_list = monarch_fetcher.get_seed_neighbour_node_ids(nodes_list)
    orthopheno_id_list = monarch_fetcher.get_orthopheno_node_ids(nodes_list, 2)
    
    register_info(f'A total of {len(seed_neighbours_id_list)} first order neighbours have been found')
    register_info(f'A total of {len(orthopheno_id_list)} orthologs/phenotypes have been found.')
    
    all_nodes_id_list = seed_neighbours_id_list.union(orthopheno_id_list)
    all_nodes_id_list.update(nodes_list)
    register_info(f'A total of {len(all_nodes_id_list)} nodes have been found for which from and to associations will be retrieved.')
    
    all_associations = monarch_fetcher.get_seed_first_order_associations(all_nodes_id_list)
    
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
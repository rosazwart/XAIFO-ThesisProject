import util.loaders as loaders
import util.monarch_fetcher as monarch_fetcher
import util.graph_builder as graph_builder
import util.mapper as mapper
import util.cypher_query_builder as cypher_query_builder

def analyzeData(all_edges, all_nodes):
    """
        Analyze given data by getting all unique properties and semantic groups, unique triplets etc.
        :param all_edges: dataframe of edges in the format resulting from BioKnowledgeReviewer Monarch Module
        :param all_nodes: dataframe of nodes in the format resulting from BioKnowledgeReviewer Monarch module
    """
    # Get all unique properties and semantic groups
    property_grouped = all_edges['property_label'].unique()
    print(f'There are {len(property_grouped)} properties:')
    print(property_grouped, '\n')
    semantic_grouped = all_nodes['semantic_groups'].unique()
    print(f'There are {len(semantic_grouped)} semantic groups:')
    print(semantic_grouped, '\n')
    
    # Retrieve relations and their subjects/objects
    edge_entries = all_edges[['subject_id', 'property_label', 'object_id']]
    
    joined_subjects = edge_entries.merge(all_nodes, left_on='subject_id', right_on='id')[['semantic_groups', 'property_label', 'object_id']]
    joined_subjects.rename(columns={'semantic_groups': 'semantic_groups_subject'}, inplace=True)
    
    joined_objects = joined_subjects.merge(all_nodes, left_on='object_id', right_on='id')[['semantic_groups_subject', 'property_label', 'semantic_groups']]
    joined_objects.rename(columns={'semantic_groups': 'semantic_groups_object'}, inplace=True)
    
    # Look at unique subject/object pairs and relation pairs
    subject_object_pairs = joined_objects[['semantic_groups_subject', 'semantic_groups_object']].drop_duplicates().reset_index(drop=True)
    
    graph_builder.draw_graph_from_edges(subject_object_pairs, source_colname='semantic_groups_subject', target_colname='semantic_groups_object', file_name='allconcepts.png')
    
    subject_property_object_triplets = joined_objects.drop_duplicates().reset_index(drop=True)
    subject_property_object_triplets = subject_property_object_triplets.sort_values(by='property_label').reset_index(drop=True)
    
    subject_property_object_triplets.rename(columns={'semantic_groups_subject': 'subject', 'property_label': 'relation', 'semantic_groups_object': 'object'}, inplace=True)
    all_col_names = list(subject_property_object_triplets.columns.values)
    for col_name in all_col_names:
        subject_property_object_triplets[col_name] = subject_property_object_triplets[col_name].str.replace('_',' ')
        subject_property_object_triplets[col_name] = subject_property_object_triplets[col_name].fillna('undefined')
        
    subject_property_object_triplets.to_csv('output/alltriplets.csv', index=False)

if __name__ == "__main__":
    # Load the edges and nodes of the graph generated from Monarch
    #all_edges = loaders.load_edges_from_csv()
    #all_nodes = loaders.load_nodes_from_csv()
    
    #analyzeData(all_edges, all_nodes)

    # Majority of ID entries lead to other semantic groups like phenotype and gene?
    #print(loaders.load_entity_sample(all_nodes, 'GENO'))
    
    nodes_list = [
        'MONDO:0010679',
        'HGNC:2928'
    ]
    
    
    seed_neighbours_id_list = monarch_fetcher.get_seed_neighbour_node_ids(nodes_list)
    orthopheno_id_list = monarch_fetcher.get_orthopheno_node_ids(nodes_list, 2)
    print(f'/nA total of {len(seed_neighbours_id_list)} first order neighbours have been found')
    print(f'A total of {len(orthopheno_id_list)} orthologs/phenotypes have been found.')
    
    associated_nodes_id_list = seed_neighbours_id_list.union(orthopheno_id_list)
    associated_nodes_id_list.update(nodes_list)
    print(f'A total of {len(associated_nodes_id_list)} associated nodes have been found.')
    
    # TODO: get neighbours of above list of nodes
    # TODO: create knowledge graph
    
    
    #seeded_graph = graph_builder.KnowledgeGraph(seed_associations)
    
    #seeded_graph_edges, seeded_graph_nodes = seeded_graph.generate_dataframes()
    
    #mapped_nodes_edges = mapper.Mapper(all_nodes=seeded_graph_nodes, all_edges=seeded_graph_edges)
    #mapped_nodes_edges.include_genotype_gene_relations()
    
    # Save into csv files
    #mapped_nodes_edges.all_edges.to_csv('output/seeded_graph_edges.csv', index=False)
    #mapped_nodes_edges.all_nodes.to_csv('output/seeded_graph_nodes.csv', index=False)
    
    #cypher_query_builder.build_queries(mapped_nodes_edges.all_nodes, mapped_nodes_edges.all_edges)
    
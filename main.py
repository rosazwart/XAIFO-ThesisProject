import util.loaders as loaders
import util.monarch_fetcher as monarch_fetcher
import util.graph_builder as graph_builder

def analyzeData(all_edges, all_nodes):
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
    
    graph_builder.create_graph(subject_object_pairs, source_colname='semantic_groups_subject', target_colname='semantic_groups_object', file_name='allconcepts.png')
    
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
    
    monarch_requester = monarch_fetcher.MonarchFetcher()
    
    #seed_associations = monarch_requester.get_seed_first_neighbour_associations(nodes_list) + monarch_requester.get_orthopheno_associations(nodes_list, 2)
    
    seed_associations = monarch_requester.get_seed_first_neighbour_associations(nodes_list)
    seeded_graph = graph_builder.KnowledgeGraph(seed_associations)
    
    seeded_graph_edges, seeded_graph_nodes = seeded_graph.generate_dataframes()
    seeded_graph_edges.to_csv('output/seeded_graph_edges.csv', index=False)
    seeded_graph_nodes.to_csv('output/seeded_graph_nodes.csv', index=False)
    
    print(seeded_graph_edges)
    print(seeded_graph_nodes)
    
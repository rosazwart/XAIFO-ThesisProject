import util.loaders as loaders
import util.monarch_fetcher as monarch_fetcher

if __name__ == "__main__":
    # Load the edges and nodes of the graph generated from Monarch
    all_edges = loaders.load_edges_from_csv()
    all_nodes = loaders.load_nodes_from_csv()
    
    property_grouped = all_edges['property_label'].unique()
    print(property_grouped)
    semantic_grouped = all_nodes['semantic_groups'].unique()
    print(semantic_grouped)

    # Majority of ID entries lead to other semantic groups like phenotype and gene?
    print(loaders.load_entity_sample(all_nodes, 'GENO'))
    print(loaders.load_entity_sample(all_nodes, 'ORTH'))
    
    node_lists = [
        'MONDO:0010679'
    ]
    
    for node in node_lists:
        monarch_requester = monarch_fetcher.MonarchFetcher()
        results_from, results_to = monarch_requester.getFromToAssociations(node=node)
        
        print(results_from.keys())
        
        print(results_from['associations'][1])
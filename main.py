import util.loaders as loaders

if __name__ == "__main__":
    # Load the edges and nodes of the graph generated from Monarch
    all_edges = loaders.load_edges_from_csv()
    all_nodes = loaders.load_nodes_from_csv()
    
    property_grouped = all_edges['property_label'].unique()
    #print(property_grouped)
    
    semantic_grouped = all_nodes['semantic_groups'].unique()
    #print(semantic_grouped)
    
    # Majority of ID entries lead to other semantic groups like phenotype and gene?
    all_genotypes = all_nodes.loc[all_nodes['semantic_groups'] == 'GENO'].sample(n=5)
    print(all_genotypes)

import monarch

if __name__ == "__main__":
    # prepare data to graph schema
    # seed nodes

    seedList = [ 
        'MONDO:0010679', #Duchenne Muscular Distrophy
    #     'MONDO:0010311', #Becker Muscular Distrophy
    #     'MONDO:0010542', #Dilated Cardiomiopathy 3B
    #     'MONDO:0016097', #Asymtomatic Female Carrier
        'HGNC:2928', #DMD human gene
    #     'MGI:94909' #DMD mouse gene
    ] 

    # get first shell of neighbours
    neighboursList = monarch.get_neighbours_list(seedList)  # 2000 rows
    print(len(neighboursList))

    # introduce animal model ortho-phenotypes for seed and 1st shell neighbors
    ## For seed nodes:
    seed_orthophenoList = monarch.get_orthopheno_list(seedList)
    print(len(seed_orthophenoList))
    ## For 1st shell nodes:
    neighbours_orthophenoList = monarch.get_orthopheno_list(neighboursList)
    print(len(neighbours_orthophenoList))

    # network nodes: seed + 1shell + ortholog-phentoype
    geneList = sum([seedList,
                    neighboursList,
                    seed_orthophenoList,
                    neighbours_orthophenoList], 
                [])
    print('genelist: ',len(geneList))

    # get Monarch network
    monarch_network = monarch.extract_edges(geneList)
    print('network: ',len(monarch_network))

    # save edges
    monarch.print_network(monarch_network, 'monarch_connections')

    # build network with graph schema 
    monarch_edges = monarch.build_edges(monarch_network)
    monarch_nodes = monarch.build_nodes(monarch_network)
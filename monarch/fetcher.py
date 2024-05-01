"""
    Module that fetches relevant data from the Monarch Initiative data and analytic platform (https://monarchinitiative.org/about/monarch).
"""
import util.constants as constants
from util.common import tuplelist2dataframe, register_info, today

import monarch.unpacker as unpacker
import monarch.filterer as filterer

def get_seed_first_order_associations(seed_id_list: list, rows: int, exclude_new_ids: bool = False):
    """
        Get list of tuples storing each association found with given seed ids.
        :param seed_id_list: list of entities represented by their identifiers
        :return: list of tuples storing associations
    """
    register_info('Associations of seeds retrieval has started...')
    direct_neighbours_associations = unpacker.get_neighbour_associations(id_list=seed_id_list, rows=rows, exclude_new_ids=exclude_new_ids)
    register_info(f'A total of {len(direct_neighbours_associations)} associations have been found between seeds and their neighbours.')
    
    return direct_neighbours_associations

def get_seed_neighbour_node_ids(seed_id_list: list, rows: int):
    """
        Get a list of all node ids of all first order neighbours of given seeds.
        :param seed_id_list: list of entities represented by their identifiers
        :return: list of neighbour node ids
    """
    register_info('Neighbours of seeds retrieval has started...')
    
    direct_neighbours_associations = unpacker.get_neighbour_associations(id_list=seed_id_list, rows=rows)
    register_info(f'A total of {len(direct_neighbours_associations)} associations have been found between seeds and their neighbours.')
    
    neighbour_ids = unpacker.get_neighbour_ids(seed_list=seed_id_list, associations=direct_neighbours_associations)
    register_info(f'A total of {len(neighbour_ids)} neighbour nodes have been found for the {len(seed_id_list)} given seeds.')
    
    return neighbour_ids
        
def get_orthopheno_node_ids(first_seed_id_list: list, depth: int, rows: int):
    """
        Get list of all nodes ids yielded from associations between an ortholog gene and phenotype. In the first iteration, orthologs are found for given seed list.
        :param first_seed_id_list: list of entities that are the seeds of first iteration
        :param depth: number of iterations
    """
    register_info('Orthologs/phenotypes retrieval has started...')
    
    all_sets = list()
    
    # Initial iteration seed list
    seed_list = first_seed_id_list
    
    for d in range(depth):   
        if (d+1 > 1):
            print(f'At depth {d+1}, replace previous list of seeds with all their first order neighbours.')
        register_info(f'For depth {d+1} seed list contains {len(seed_list)} ids')
        
        # Get associations between seeds and their first order neighbours
        direct_neighbours_associations = unpacker.get_neighbour_associations(id_list=seed_list, rows=rows)
        # Get all ids of found neighbour nodes
        neighbour_id_list = unpacker.get_neighbour_ids(seed_list=seed_list, associations=direct_neighbours_associations)
        register_info(f'{len(neighbour_id_list)} neighbours of given seeds')
        
        # Filter to only include associations related to orthology
        associations_with_orthologs = filterer.get_associations_on_relations(direct_neighbours_associations, 'orthologous')
        
        # Free memory as this list is not used anymore in this iteration
        direct_neighbours_associations = []
        
        # Get all orthologs of genes included in given list of ids
        ortholog_id_list = unpacker.get_neighbour_ids(seed_list=seed_list, associations=associations_with_orthologs, include_semantic_groups=['gene'])
        register_info(f'{len(ortholog_id_list)} orthologous genes of given seeds')
        
        # Get the first layer of neighbours of orthologs
        ortholog_associations = unpacker.get_neighbour_associations(id_list=ortholog_id_list, rows=rows);
        # Filter to only include associations related to phenotype
        phenotype_id_list = unpacker.get_neighbour_ids(seed_list=ortholog_id_list, associations=ortholog_associations, include_semantic_groups=['phenotype'])
        register_info(f'{len(phenotype_id_list)} phenotypes of orthologous genes')
        
        # Free memory as this list is not used anymore in this iteration
        ortholog_associations = []
        
        # Add set of ortholog nodes of seeds
        all_sets.append(ortholog_id_list)
        all_sets.append(phenotype_id_list)
        
        register_info(f'{len(ortholog_id_list)+len(phenotype_id_list)} orthologs/phenotypes')
        
        # Next iteration seed list
        seed_list = neighbour_id_list
    
    all_ortho_pheno_node_ids = set().union(*all_sets)
    register_info(f'{len(all_ortho_pheno_node_ids)} orthologs/phenotypes have been found using a depth of {depth}')
    
    return all_ortho_pheno_node_ids
    
def get_monarch_associations(nodes_list):
    
    seed_neighbours_id_list = get_seed_neighbour_node_ids(seed_id_list=nodes_list, rows=2000)
    orthopheno_id_list = get_orthopheno_node_ids(first_seed_id_list=nodes_list, depth=2, rows=2000)
    
    register_info(f'A total of {len(seed_neighbours_id_list)} first order neighbours of given seeds have been found')
    register_info(f'A total of {len(orthopheno_id_list)} orthologs/phenotypes have been found.')
    
    all_nodes_id_list = seed_neighbours_id_list.union(orthopheno_id_list)
    all_nodes_id_list.update(nodes_list)
    register_info(f'A total of {len(all_nodes_id_list)} nodes have been found for which from and to associations will be retrieved.')
        
    all_associations = get_seed_first_order_associations(seed_id_list=all_nodes_id_list, rows=1000, exclude_new_ids=True)
    
    tuplelist2dataframe(all_associations).to_csv(f'{constants.OUTPUT_FOLDER}/monarch_associations_{today}.csv', index=False)
    register_info(f'All MONARCH associations are saved into monarch_associations_{today}.csv')
    
    return all_associations
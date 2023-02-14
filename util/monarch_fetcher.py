"""
    Module that fetches relevant data from the Monarch Initiative data and analytic platform (https://monarchinitiative.org/about/monarch).
"""

import requests
from tqdm import tqdm

BASE_URL = 'https://api.monarchinitiative.org/api'
relation_ids_filters = {'orthologous': ['RO:HOM0000017', 'RO:HOM0000020']}

def get_in_out_associations(node: str, params: dict, max_rows: int = 2000):
    """
        Get all out and in edges of given node. 
        :param node: identifier of node
        :param max_rows: maximum number of rows to get
        :return: responses of getting out and in associations, respectively
    """
    params['rows'] = max_rows
    
    response_out = requests.get(f'{BASE_URL}/association/from/{node}', params=params)
    response_in = requests.get(f'{BASE_URL}/association/to/{node}', params=params)
    
    try:
        return response_out.json(), response_in.json()
    except Exception as e:
        print(e)
        print('node', node)
        print('response in', response_in)
        print('response out', response_out)
        raise Exception('NOPE')
    
def get_filtered_associations_on_entities(all_associations: list, semantic_groups_filter: list, include: bool = True):
    """
        Get a filtered list of associations in which each association includes at least one entity that belongs to
        one of the given semantic groups.
        :param all_associations: list of associations that needs to be filtered
        :param include_semantic_groups: list of semantic groups that needs to be included
        :return: list of filtered associations
    """
    filtered_associations = list()

    for association in all_associations:
        all_semantic_groups = association['subject']['category'] + association['object']['category']
        intersection = [semantic_group for semantic_group in all_semantic_groups if semantic_group in semantic_groups_filter]
        
        if (include and len(intersection) > 0) or (not include and len(intersection) == 0):
            filtered_associations.append(association)
            
    return filtered_associations
    
def get_filtered_associations_on_relations(all_associations: list, include_relation_ids_group: list):
    """
        Get a filtered list of associations in which each association includes one of the given relations.
        :param all_associations: list of associations
        :param include_relation_ids_group: list of relation ids that needs to be included
        :return: list of filtered associations
    """
    filtered_associations = list()
    
    for association in all_associations:
        if (association['relation']['id'] in relation_ids_filters[include_relation_ids_group]):
            filtered_associations.append(association)
            
    return filtered_associations
    
def unpack_response(response_values):
    """
        Association information is embedded in response, so unpack this information from nonrelevant values.
        :param response_value: dictionary with BioLink API response objects
        :return: list of association dictionaries
    """
    unpacked_associations = list()
    
    if ('associations' in response_values.keys()):   
        for response in response_values['associations']:
            unpacked_associations.append(response)
            
    return unpacked_associations
    
def get_neighbour_ids(seed_list: list, associations: list, include_semantic_groups: list = []):
    """
        Get all ids of list of associations that are not the seed ids. If given, only include ids when entity belongs to at least
        one of given semantic groups.
        :param seed_list: list of seed ids
        :param associations: list of associations
        :param include_semantic_groups: list of semantic groups to which all neighbour ids need to belong
        :return: list of (filtered) neighbour ids 
    """
    neighbour_ids = set()
    
    for association in associations:
        subject_node_id = association['subject']['id']
        object_node_id = association['object']['id']
        
        subject_intersection = [semantic_group for semantic_group in association['subject']['category'] if semantic_group in include_semantic_groups]
        if not(subject_node_id in seed_list) and len(subject_intersection) > 0:
            neighbour_ids.add(subject_node_id)
        
        object_intersection = [semantic_group for semantic_group in association['object']['category'] if semantic_group in include_semantic_groups]
        if not(object_node_id in seed_list) and len(object_intersection) > 0:
            neighbour_ids.add(object_node_id)
        
    return neighbour_ids
        
def get_neighbour_associations(id_list: list, relations: list = []):
    """ 
        Return the first layer of neighbours from a list of node identifiers.
        :param id_list: list of entities represented by their identifiers
        :return: list of direct neighbours
    """
    all_associations = []
    
    all_seed_nodes = set(id_list)
    for seed_node in tqdm(all_seed_nodes):
        params = {}
        
        if (len(relations) > 0):
            for relation_id in relations:
                params['relation'] = relation_id
                
                response_assoc_out, response_assoc_in = get_in_out_associations(seed_node, params)
                
                assoc_out = unpack_response(response_assoc_out)
                assoc_in = unpack_response(response_assoc_in)
                
                all_associations = all_associations + assoc_out + assoc_in
        else:
            response_assoc_out, response_assoc_in = get_in_out_associations(seed_node, params)
            
            assoc_out = unpack_response(response_assoc_out)
            assoc_in = unpack_response(response_assoc_in)
            
            all_associations = all_associations + assoc_out + assoc_in
        
    return get_filtered_associations_on_entities(all_associations, ['publication'], include=False)
    
def get_seed_first_neighbour_associations(id_list: list):
    """
        Get a list of all associations with all first neighbours of given seeds.
        :param id_list: list of entities represented by their identifiers
        :return: object with nodes and edges 
    """
    # Retrieve the first layer of neighbours
    direct_neighbours_associations = get_neighbour_associations(id_list)
    print(f'{len(direct_neighbours_associations)} directly neighbouring associations of seeds')
    
    return direct_neighbours_associations
        
def get_orthopheno_associations(first_seed_id_list: list, depth: int):
    """
        Get list of associations between an ortholog gene and phenotype. These genes are orthologous to initial entities given.
        :param first_seed_id_list: list of entities that are the first seeds
        :param depth: number of iterations
    """
    all_ortho_pheno_associations = []
    
    seed_list = first_seed_id_list
    for d in range(depth):   
        if (depth > 0):
            print(f'At depth {d+1}, replace previous list of seeds with their first order ortholog neighbours.')
        print(f'Seed list contains {len(seed_list)} seeds')
        
        # Retrieve the first layer of neighbours
        direct_neighbours_associations = get_neighbour_associations(seed_list)
        print(f'{len(direct_neighbours_associations)} directly neighbouring associations of seeds')
        
        # Filter to only include associations related to orthology
        seed_associations_with_orthologs = get_filtered_associations_on_relations(direct_neighbours_associations, 'orthologous')
        
        # Retrieve all orthologs of genes included in given list of ids
        ortholog_id_list = get_neighbour_ids(seed_list, seed_associations_with_orthologs, ['gene'])
        print(f'{len(ortholog_id_list)} orthologous genes of the given seeds')
        
        # Retrieve the first layer of neighbours of orthologs
        ortholog_associations = get_neighbour_associations(ortholog_id_list);
        print(f'{len(ortholog_associations)} directly neighbouring associations of seed orthologs')
        
        # Filter to only include associations related to phenotype
        ortholog_associations_with_phenotypes = get_filtered_associations_on_entities(ortholog_associations, ['phenotype'])
        print(f'{len(ortholog_associations_with_phenotypes)} phenotype associations of seed orthologs')
        
        # Add newly retrieved ortho-pheno associations to list
        all_ortho_pheno_associations = all_ortho_pheno_associations + seed_associations_with_orthologs + ortholog_associations_with_phenotypes
        
        # Get direct neighbours of seeds that are the new seeds in next iteration
        neighbour_id_list = get_neighbour_ids(seed_list, direct_neighbours_associations, ['gene'])
        print(f'{len(neighbour_id_list)} direct neighbours of seeds being a gene')
        seed_list = neighbour_id_list
    
    return all_ortho_pheno_associations
    
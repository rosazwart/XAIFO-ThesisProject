"""
    This module unpacks responses of the BioLink API to relevant data structures.
"""

from tqdm import tqdm

import util.constants as constants
import monarch.requester as requester
import monarch.filterer as filterer

def load_into_tuple(association_info):
    """
        Load relevant dictionary values into a tuple. Use defined tuple value names `constants.assoc_tuple_values` to navigate through association dictionary.
        :param association_info: dictionary of information about association
        :return: tuple of association information values
    """
    info_list = list()
    for assoc_tuple_value in constants.assoc_tuple_values:
        dict_levels = assoc_tuple_value.split('_')
        
        value = association_info
        for dict_level in dict_levels:
            if dict_level == 'category':
                value = value[dict_level][0]    # only allow one category, first category of list of categories chosen
            else:
                value = value[dict_level]
        
        info_list.append(value)
        
    return tuple(info_list)

def unpack_response(response_values, seed_id_list = None):
    """
        Association information is embedded in response, so unpack this information from nonrelevant values. Store each association entry in a tuple.
        :param response_value: dictionary with BioLink API response objects
        :param seed_id_list: when list of seeds is given, exclude all associations that introduce nodes not existing in seeds list
        :return: list of association dictionaries
    """
    unpacked_associations = list()
    
    if ('associations' in response_values.keys()):   
        for association in response_values['associations']:
            # Tuple contains the following info: id, subject_id, 
            association_info = load_into_tuple(association)
            
            if seed_id_list:
                subject_id = association_info[constants.assoc_tuple_values.index('subject_id')]
                object_id = association_info[constants.assoc_tuple_values.index('object_id')]
                
                if {subject_id, object_id} <= seed_id_list:
                    unpacked_associations.append(association_info)
            else:
                unpacked_associations.append(association_info)
            
    return unpacked_associations
    
def get_neighbour_ids(seed_list: list, associations: list, include_semantic_groups: list = []):
    """
        Get all ids of list of associations that are not the seed ids. If given, only include ids when entity belongs to at least
        one of given semantic groups.
        :param seed_list: list of seed ids
        :param associations: list of associations
        :param include_semantic_groups: list of semantic groups to which all neighbour ids need to belong
        :return: set of (filtered) neighbour ids 
    """
    neighbour_ids = set()
    
    for association in associations:
        subject_node_id = association[constants.assoc_tuple_values.index('subject_id')] 
        object_node_id = association[constants.assoc_tuple_values.index('object_id')] 
        
        if not(subject_node_id in seed_list) and (len(include_semantic_groups) == 0 or association[constants.assoc_tuple_values.index('subject_category')] in include_semantic_groups):
            neighbour_ids.add(subject_node_id)
        
        if not(object_node_id in seed_list) and (len(include_semantic_groups) == 0 or association[constants.assoc_tuple_values.index('object_category')] in include_semantic_groups):
            neighbour_ids.add(object_node_id)
        
    return neighbour_ids
        
def get_neighbour_associations(id_list: list, rows: int = 2000, relations: list = [], exclude_new_ids: bool = False):
    """ 
        Return the first layer of neighbours from a list of node identifiers.
        :param id_list: list of entities represented by their identifiers
        :param relations: when parsing a non-empty list, these elements are the relation ids such that only associations are retrieved including these relations
        :return: list of direct neighbours (list of tuples)
    """
    all_associations = set()
    all_seed_nodes = set(id_list)   # make sure there are no duplicate seed ids
    
    if exclude_new_ids:
        included_id_list = all_seed_nodes
    else:
        included_id_list = None
    
    for seed_node in tqdm(all_seed_nodes):
        params = {}
        
        if (len(relations) > 0):
            for relation_id in relations:
                params['relation'] = relation_id
                
                response_assoc_out, response_assoc_in = requester.get_in_out_associations(seed_node, params, rows)
                
                assoc_out = unpack_response(response_assoc_out, included_id_list)
                assoc_in = unpack_response(response_assoc_in, included_id_list)
                
                all_associations.update(assoc_out)
                all_associations.update(assoc_in)
        else:
            response_assoc_out, response_assoc_in = requester.get_in_out_associations(seed_node, params, rows)
            
            assoc_out = unpack_response(response_assoc_out, included_id_list)
            assoc_in = unpack_response(response_assoc_in, included_id_list)
            
            all_associations.update(assoc_out)
            all_associations.update(assoc_in)
        
    return filterer.get_associations_on_entities(all_associations, ['publication'], include=False)